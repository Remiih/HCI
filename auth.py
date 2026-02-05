import pyotp
import qrcode
from passlib.context import CryptContext
import io

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def generate_totp_secret():
    return pyotp.random_base32()

def get_totp_uri(username, secret):
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name="InventoryApp"
    )

def verify_totp(secret, code):
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

def generate_qr_code(uri):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes for Streamlit
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

import re

def validate_password(password):
    """
    Validates that the password meets the following criteria:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[ !@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
        return False, "Password must contain at least one special character."
    if len(password.encode('utf-8')) > 72:
        return False, "Password is too long (max 72 bytes)."
        
    return True, "Password is valid."

def validate_username(username):
    """
    Validates that the username:
    - Is 3-20 characters long
    - Contains only alphanumeric characters, underscores, or hyphens
    - No spaces
    """
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be between 3 and 20 characters."
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens (no spaces)."
    return True, "Username is valid."
