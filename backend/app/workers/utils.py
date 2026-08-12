import asyncio
from collections.abc import Awaitable, Callable, AsyncGenerator
from contextlib import asynccontextmanager
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import AsyncSessionLocal

T = TypeVar("T")


def run_async(coro_fn: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
    """Celery tasks are sync; our services are async. Each task invocation
    gets its own short-lived event loop rather than sharing one across tasks,
    which keeps worker processes simple and avoids loop-lifetime bugs."""
    return asyncio.run(coro_fn(*args, **kwargs))


@asynccontextmanager
async def worker_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
