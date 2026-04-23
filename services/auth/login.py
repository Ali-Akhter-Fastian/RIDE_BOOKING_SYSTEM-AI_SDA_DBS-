from __future__ import annotations

from core.security import create_access_token, create_refresh_token, verify_password
from exception.auth_exceptions import InvalidCredentials
from schemas.auth import LoginRequest, TokenResponse

from .base import AuthServiceBase


class LoginAuthService(AuthServiceBase):
    async def login_user(self, payload: LoginRequest) -> TokenResponse:
        user = await self.repository.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise InvalidCredentials("Invalid email or password")

        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value},
            secret_key=self.settings.jwt_secret,
            algorithm=self.settings.jwt_algorithm,
            expires_delta_minutes=self.settings.access_token_expire_minutes,
        )

        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value},
            secret_key=self.settings.jwt_secret,
            algorithm=self.settings.jwt_algorithm,
            expires_delta_minutes=self.settings.refresh_token_expire_minutes,
        )

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
