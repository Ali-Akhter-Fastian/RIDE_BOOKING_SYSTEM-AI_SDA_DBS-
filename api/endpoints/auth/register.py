from __future__ import annotations

from fastapi import APIRouter, Depends, status

from schemas.auth import RegisterRequest, UserResponse

from .dependencies import get_register_auth_service
from services.auth import RegisterAuthService
from exception.auth_exceptions import raise_auth_http_exception

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: RegisterRequest, # validates the request body against auth.py, if the payload(request body) is invalid, the request never reaches your service.
    service: RegisterAuthService = Depends(get_register_auth_service),
) -> UserResponse:
    try:
        user = await service.register_user(payload)
    except Exception as exc:
        raise_auth_http_exception(exc)
    return UserResponse.model_validate(user)
