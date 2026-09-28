import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Deliberately loose: real validation is "can they receive mail there",
# which a regex can't answer.
_EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

# bcrypt only looks at the first 72 bytes of a password.
_BCRYPT_MAX_BYTES = 72


class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=320, pattern=_EMAIL_PATTERN)
    password: str = Field(..., min_length=8)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: Any) -> Any:
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        if len(value.encode()) > _BCRYPT_MAX_BYTES:
            raise ValueError(f"Password must be at most {_BCRYPT_MAX_BYTES} bytes")
        return value


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=320)
    password: str = Field(..., min_length=1, max_length=_BCRYPT_MAX_BYTES * 4)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead
