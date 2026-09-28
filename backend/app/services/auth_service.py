import asyncio
import uuid
from functools import lru_cache

from app.core.exceptions import AuthError, ConflictError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest


@lru_cache
def _dummy_password_hash() -> str:
    return hash_password("not-a-real-password")


class AuthService:
    """
    Account signup and password login. bcrypt is deliberately slow, so
    hashing/verification runs in a worker thread to keep the event loop free.
    """

    def __init__(self, users: UserRepository):
        self.users = users

    async def register(self, data: RegisterRequest) -> User:
        if await self.users.get_by_email(data.email) is not None:
            raise ConflictError("An account with this email already exists")
        password_hash = await asyncio.to_thread(hash_password, data.password)
        return await self.users.create(data.email, password_hash)

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.users.get_by_email(email.strip().lower())
        # Verify against a dummy hash for unknown emails too, so response
        # timing doesn't reveal which emails have accounts.
        password_hash = user.password_hash if user is not None else _dummy_password_hash()
        password_ok = await asyncio.to_thread(verify_password, password, password_hash)
        if user is None or not password_ok or not user.is_active:
            raise AuthError("Incorrect email or password")
        return user

    async def get_active_user(self, user_id: uuid.UUID) -> User | None:
        user = await self.users.get_by_id(user_id)
        return user if user is not None and user.is_active else None
