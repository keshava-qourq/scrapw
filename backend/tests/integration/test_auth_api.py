import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_auth_service
from app.core.exceptions import ConflictError
from app.main import app
from app.models.user import User
from app.services.auth_service import AuthService


class FakeUserRepository:
    """In-memory stand-in for UserRepository, so the real AuthService (and
    real password hashing / JWT handling) run without a database."""

    def __init__(self):
        self.users: dict[uuid.UUID, User] = {}

    async def get_by_id(self, user_id):
        return self.users.get(user_id)

    async def get_by_email(self, email):
        return next((u for u in self.users.values() if u.email == email), None)

    async def create(self, email, password_hash):
        if await self.get_by_email(email) is not None:
            raise ConflictError("An account with this email already exists")
        user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash=password_hash,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        self.users[user.id] = user
        return user


@pytest.fixture
def client(real_auth):
    repo = FakeUserRepository()
    app.dependency_overrides[get_auth_service] = lambda: AuthService(repo)
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_auth_service, None)


def _register(client, email="Shopper@Example.com", password="s3cure-passw0rd"):
    return client.post("/api/v1/auth/register", json={"email": email, "password": password})


def test_register_returns_token_that_authenticates_me(client):
    response = _register(client)
    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "shopper@example.com"

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "shopper@example.com"


def test_register_duplicate_email_is_conflict(client):
    _register(client)
    response = _register(client, email="shopper@example.com")
    assert response.status_code == 409


def test_register_rejects_short_password(client):
    response = _register(client, password="short")
    assert response.status_code == 422


def test_login_with_correct_password(client):
    _register(client)
    response = client.post(
        "/api/v1/auth/login", json={"email": "SHOPPER@example.com", "password": "s3cure-passw0rd"}
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_with_wrong_password_or_unknown_email_is_401(client):
    _register(client)
    wrong_password = client.post(
        "/api/v1/auth/login", json={"email": "shopper@example.com", "password": "nope-nope-nope"}
    )
    unknown_email = client.post(
        "/api/v1/auth/login", json={"email": "nobody@example.com", "password": "s3cure-passw0rd"}
    )
    assert wrong_password.status_code == 401
    assert unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()


def test_protected_route_requires_token(client):
    assert client.get("/api/v1/watchlist/groups").status_code == 401
    assert client.get("/api/v1/auth/me").status_code == 401


def test_protected_route_rejects_invalid_token(client):
    response = client.get("/api/v1/watchlist/groups", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_health_stays_public(client):
    assert client.get("/api/v1/health").status_code == 200
