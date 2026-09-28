import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, email: str, password_hash: str) -> User:
        user = User(email=email, password_hash=password_hash)
        self.session.add(user)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            # Lost a race with a concurrent signup for the same email.
            await self.session.rollback()
            raise ConflictError("An account with this email already exists") from exc
        await self.session.refresh(user)
        return user
