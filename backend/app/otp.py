from __future__ import annotations

import pyotp


def generate_otp(secret: str, digits: int = 6, period: int = 30) -> str:
    totp = pyotp.TOTP(s=secret, digits=digits, interval=period)
    return totp.now()

