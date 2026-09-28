import uuid
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.config import get_settings
from app.core.exceptions import AuthError
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_round_trip():
    password_hash = hash_password("correct horse battery staple")
    assert password_hash != "correct horse battery staple"
    assert verify_password("correct horse battery staple", password_hash)
    assert not verify_password("wrong password", password_hash)


def test_access_token_round_trip():
    user_id = uuid.uuid4()
    token, expires_in = create_access_token(user_id)
    assert expires_in == get_settings().access_token_expire_minutes * 60
    assert decode_access_token(token) == user_id


def test_expired_token_is_rejected():
    settings = get_settings()
    payload = {"sub": str(uuid.uuid4()), "exp": datetime.now(timezone.utc) - timedelta(seconds=1)}
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    with pytest.raises(AuthError):
        decode_access_token(token)


def test_token_signed_with_another_key_is_rejected():
    payload = {"sub": str(uuid.uuid4()), "exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
    token = jwt.encode(payload, "some-other-secret", algorithm="HS256")
    with pytest.raises(AuthError):
        decode_access_token(token)


def test_garbage_token_is_rejected():
    with pytest.raises(AuthError):
        decode_access_token("not-a-jwt")
