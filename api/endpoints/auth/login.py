from __future__ import annotations

from fastapi import APIRouter, Depends

from schemas.auth import LoginRequest, TokenResponse
from exception.auth_exceptions import raise_auth_http_exception
from services.auth import LoginAuthService

from .dependencies import get_login_auth_service

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login_user(
    payload: LoginRequest,
    service: LoginAuthService = Depends(get_login_auth_service),
) -> TokenResponse:
    try:
        return await service.login_user(payload)
    except Exception as exc:
        raise_auth_http_exception(exc)
