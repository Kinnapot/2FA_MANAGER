import pyotp

def generate_otp(secret):
    totp = pyotp.TOTP(secret)
    return totp.now()
