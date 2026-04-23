from __future__ import annotations

from fastapi import Depends

from app.config import Settings, get_settings
from app.dependencies import get_db
from repositories.auth_repository import AuthRepository
from services.auth import LoginAuthService, RegisterAuthService, SessionAuthService


def get_register_auth_service(
    connection=Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> RegisterAuthService:
    return RegisterAuthService(AuthRepository(connection), settings)


def get_login_auth_service(
    connection=Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> LoginAuthService:
    return LoginAuthService(AuthRepository(connection), settings)


def get_session_auth_service(
    connection=Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> SessionAuthService:
    return SessionAuthService(AuthRepository(connection), settings)
