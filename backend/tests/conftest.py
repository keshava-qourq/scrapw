import os
import uuid

# Must be set before `app` is imported, since settings are cached on first use.
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-not-for-production")

import pytest  # noqa: E402

from app.api.deps import get_current_user  # noqa: E402
from app.core.rate_limit import limiter  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402

FAKE_USER = User(id=uuid.uuid4(), email="tester@example.com", password_hash="unused", is_active=True)


@pytest.fixture(autouse=True)
def logged_in_user():
    """Most API tests exercise a route's behaviour, not auth, so they run as a
    logged-in fake user. Auth tests opt out via the `real_auth` fixture."""
    app.dependency_overrides[get_current_user] = lambda: FAKE_USER
    yield FAKE_USER
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def real_auth(logged_in_user):
    app.dependency_overrides.pop(get_current_user, None)
    limiter.reset()
    yield
    limiter.reset()
