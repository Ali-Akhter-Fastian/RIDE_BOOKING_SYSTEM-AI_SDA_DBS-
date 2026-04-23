from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from core.security import hash_password
from exception.auth_exceptions import UserExists
from models.user import User
from repositories.auth_repository import AuthRepository
from schemas.auth import RegisterRequest

from .base import AuthServiceBase


class RegisterAuthService(AuthServiceBase):
    async def register_user(self, payload: RegisterRequest) -> User:
        existing_user = await self.repository.get_by_email(payload.email)
        if existing_user is not None:
            raise UserExists("User already exists")

        now = datetime.now(timezone.utc)
        user = User(
            id=uuid4(),
            full_name=payload.full_name,
            email=payload.email.lower(),
            password_hash=hash_password(payload.password),
            role=payload.role,
            created_at=now,
            updated_at=now,
        )
        return await self.repository.create(user)
