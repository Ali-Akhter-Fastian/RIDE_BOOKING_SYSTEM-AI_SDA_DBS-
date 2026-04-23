from __future__ import annotations

from typing import AsyncIterator
from uuid import UUID

import asyncpg
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings, get_settings
from core.security import decode_access_token
from exception.auth_exceptions import TokenError
from models.user import User
from repositories.auth_repository import AuthRepository

bearer_scheme = HTTPBearer(auto_error=True)


async def get_db(request: Request) -> AsyncIterator[asyncpg.Connection]:
    pool = getattr(request.app.state, "db_pool", None)
    if pool is None:
        raise RuntimeError("Database pool is not initialized")

    async with pool.acquire() as connection:
        yield connection


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    connection: asyncpg.Connection = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> User:
    try:
        payload = decode_access_token(
            token=credentials.credentials,
            secret_key=settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    subject = payload.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")

    try:
        user_id = UUID(subject)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token") from exc

    repository = AuthRepository(connection)
    user = await repository.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
