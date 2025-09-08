from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, LargeBinary, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    note: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    password_enc: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    secret_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    digits: Mapped[int] = mapped_column(Integer, default=6, nullable=False)
    period: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

