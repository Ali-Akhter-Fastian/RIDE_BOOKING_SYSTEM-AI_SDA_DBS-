from __future__ import annotations

from fastapi import APIRouter, Depends

from exception.auth_exceptions import raise_auth_http_exception
from schemas.auth.session import LogoutRequest, MessageResponse
from services.auth import SessionAuthService

from .dependencies import get_session_auth_service

router = APIRouter()


@router.post("/logout", response_model=MessageResponse)
async def logout(
    payload: LogoutRequest,
    service: SessionAuthService = Depends(get_session_auth_service),
) -> MessageResponse:
    try:
        await service.logout(payload.refresh_token)
        return MessageResponse(message="Logout successful")
    except Exception as exc:
        raise_auth_http_exception(exc)
