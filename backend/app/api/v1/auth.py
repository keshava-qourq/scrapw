from fastapi import APIRouter, Depends, Request

from app.api.deps import get_auth_service, get_current_user
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_response(user: User) -> TokenResponse:
    access_token, expires_in = create_access_token(user.id)
    return TokenResponse(access_token=access_token, expires_in=expires_in, user=UserRead.model_validate(user))


@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit(lambda: get_settings().auth_rate_limit)
async def register(
    request: Request,
    data: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return _token_response(await service.register(data))


@router.post("/login", response_model=TokenResponse)
@limiter.limit(lambda: get_settings().auth_rate_limit)
async def login(
    request: Request,
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return _token_response(await service.authenticate(data.email, data.password))


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)) -> User:
    return user
