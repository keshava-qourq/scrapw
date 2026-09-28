import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import get_settings
from app.core.exceptions import AuthError


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def _secret_key() -> str:
    secret = get_settings().jwt_secret_key
    if not secret:
        raise RuntimeError("JWT_SECRET_KEY is not set — see backend/.env.example")
    return secret


def create_access_token(user_id: uuid.UUID) -> tuple[str, int]:
    """Return a signed access token for `user_id` and its lifetime in seconds."""
    settings = get_settings()
    expires_in = settings.access_token_expire_minutes * 60
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "iat": now, "exp": now + timedelta(seconds=expires_in)}
    return jwt.encode(payload, _secret_key(), algorithm=settings.jwt_algorithm), expires_in


def decode_access_token(token: str) -> uuid.UUID:
    """Return the user id a token was issued for, or raise AuthError if the
    token is malformed, tampered with, or expired."""
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            _secret_key(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp"]},
        )
        return uuid.UUID(payload["sub"])
    except (jwt.PyJWTError, ValueError) as exc:
        raise AuthError("Invalid or expired token") from exc
