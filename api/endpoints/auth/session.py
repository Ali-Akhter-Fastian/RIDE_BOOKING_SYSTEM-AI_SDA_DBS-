from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.dependencies import get_current_user
from exception.auth_exceptions import raise_auth_http_exception
from models.user import User
from schemas.auth import (
    LogoutRequest,
    MessageResponse,
    RefreshTokenRequest,
    TokenResponse,
    VerifyOtpRequest,
    VerifyOtpResponse,
)
from services.auth import SessionAuthService

from .dependencies import get_session_auth_service

router = APIRouter()


@router.post("/verify-otp", response_model=VerifyOtpResponse)
async def verify_otp(
    payload: VerifyOtpRequest,
    current_user: User = Depends(get_current_user),
    service: SessionAuthService = Depends(get_session_auth_service),
) -> VerifyOtpResponse:
    try:
        return await service.verify_otp(current_user, payload)
    except Exception as exc:
        raise_auth_http_exception(exc)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    payload: RefreshTokenRequest,
    service: SessionAuthService = Depends(get_session_auth_service),
) -> TokenResponse:
    try:
        return await service.refresh_access_token(payload)
    except Exception as exc:
        raise_auth_http_exception(exc)


@router.post("/logout", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def logout(
    payload: LogoutRequest,
    service: SessionAuthService = Depends(get_session_auth_service),
) -> MessageResponse:
    try:
        return await service.logout(payload)
    except Exception as exc:
        raise_auth_http_exception(exc)
