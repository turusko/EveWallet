import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta

from cryptography.fernet import Fernet

from app.core.config import get_settings


settings = get_settings()


def new_state() -> str:
    return secrets.token_urlsafe(32)


def sign_state(state: str) -> str:
    sig = hmac.new(settings.secret_key.encode(), state.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode()


def verify_state(state: str, signature: str) -> bool:
    expected = sign_state(state)
    return hmac.compare_digest(expected, signature)


def token_expiry(expires_in: int) -> datetime:
    return datetime.now(UTC) + timedelta(seconds=expires_in)


def encrypt_if_possible(value: str) -> str:
    if not settings.token_encryption_key:
        return value
    f = Fernet(settings.token_encryption_key.encode())
    return f.encrypt(value.encode()).decode()


def decrypt_if_possible(value: str) -> str:
    if not settings.token_encryption_key:
        return value
    f = Fernet(settings.token_encryption_key.encode())
    return f.decrypt(value.encode()).decode()
