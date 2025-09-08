from __future__ import annotations

from typing import Optional, List, Dict, Any
import os

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field as PydField
from sqlalchemy.orm import Session

from .models import Base, Account
from .db import engine, get_db
from .security import encrypt, decrypt, ensure_key
from .otp import generate_otp


class AccountCreate(BaseModel):
    username: str
    password: Optional[str] = None
    secret_key: str
    note: Optional[str] = None
    digits: int = 6
    period: int = 30


class AccountUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    secret_key: Optional[str] = None
    note: Optional[str] = None
    digits: Optional[int] = None
    period: Optional[int] = None


class AccountOut(BaseModel):
    id: str
    username: str
    note: Optional[str]
    digits: int
    period: int
    has_password: bool


def create_app() -> FastAPI:
    app = FastAPI(title="2FA Manager API")

    # CORS
    origins = os.getenv("CORS_ORIGINS", "http://localhost:8080").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in origins if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def startup():
        ensure_key()  # ensure FERNET_KEY exists
        Base.metadata.create_all(bind=engine)

    # Accounts
    @app.get("/api/accounts", response_model=List[AccountOut])
    def list_accounts(db: Session = Depends(get_db)):
        rows = db.query(Account).order_by(Account.created_at.desc()).all()
        return [
            AccountOut(
                id=a.id,
                username=a.username,
                note=a.note,
                digits=a.digits,
                period=a.period,
                has_password=a.password_enc is not None,
            )
            for a in rows
        ]

    @app.post("/api/accounts")
    def create_account(payload: AccountCreate, db: Session = Depends(get_db)):
        username = payload.username.strip()
        secret = payload.secret_key.strip().replace(" ", "")
        if not username or not secret:
            raise HTTPException(status_code=400, detail="username and secret_key are required")
        acc = Account(
            username=username,
            note=(payload.note or None),
            secret_enc=encrypt(secret),
            digits=payload.digits or 6,
            period=payload.period or 30,
        )
        if payload.password and payload.password.strip():
            acc.password_enc = encrypt(payload.password)
        db.add(acc)
        db.commit()
        return {"id": acc.id}

    @app.put("/api/accounts/{account_id}")
    def update_account(account_id: str, payload: AccountUpdate, db: Session = Depends(get_db)):
        acc = db.get(Account, account_id)
        if not acc:
            raise HTTPException(status_code=404, detail="not found")
        if payload.username is not None:
            acc.username = payload.username.strip()
        if payload.note is not None:
            acc.note = payload.note or None
        if payload.digits is not None:
            acc.digits = int(payload.digits)
        if payload.period is not None:
            acc.period = int(payload.period)
        if payload.secret_key is not None and payload.secret_key.strip():
            acc.secret_enc = encrypt(payload.secret_key.strip().replace(" ", ""))
        if payload.password is not None and payload.password.strip():
            acc.password_enc = encrypt(payload.password)
        db.add(acc)
        db.commit()
        return {"ok": True}

    @app.delete("/api/accounts/{account_id}")
    def delete_account(account_id: str, db: Session = Depends(get_db)):
        acc = db.get(Account, account_id)
        if not acc:
            raise HTTPException(status_code=404, detail="not found")
        db.delete(acc)
        db.commit()
        return {"ok": True}

    @app.get("/api/accounts/{account_id}/otp")
    def get_otp(account_id: str, db: Session = Depends(get_db)):
        acc = db.get(Account, account_id)
        if not acc:
            raise HTTPException(status_code=404, detail="not found")
        secret = decrypt(acc.secret_enc)
        otp = generate_otp(secret, digits=acc.digits, period=acc.period)
        return {"otp": otp}

    @app.get("/api/accounts/{account_id}/password")
    def get_password(account_id: str, db: Session = Depends(get_db)):
        acc = db.get(Account, account_id)
        if not acc:
            raise HTTPException(status_code=404, detail="not found")
        if not acc.password_enc:
            raise HTTPException(status_code=404, detail="password not set")
        return {"password": decrypt(acc.password_enc)}

    @app.get("/api/accounts/{account_id}/secret")
    def get_secret(account_id: str, db: Session = Depends(get_db)):
        acc = db.get(Account, account_id)
        if not acc:
            raise HTTPException(status_code=404, detail="not found")
        return {"secret_key": decrypt(acc.secret_enc)}

    return app


app = create_app()

