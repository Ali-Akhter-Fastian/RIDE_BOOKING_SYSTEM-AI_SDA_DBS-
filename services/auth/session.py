from __future__ import annotations

from core.security import create_access_token, decode_refresh_token
from exception.auth_exceptions import InvalidCredentials, InvalidOtp, TokenError
from models.user import User
from schemas.auth import LogoutRequest, MessageResponse, RefreshTokenRequest, TokenResponse, VerifyOtpRequest, VerifyOtpResponse

from .base import AuthServiceBase


class SessionAuthService(AuthServiceBase):
    async def refresh_access_token(self, payload: RefreshTokenRequest) -> TokenResponse:
        token_payload = decode_refresh_token(
            token=payload.refresh_token,
            secret_key=self.settings.jwt_secret,
            algorithm=self.settings.jwt_algorithm,
        )

        subject = token_payload.get("sub")
        email = token_payload.get("email")
        role = token_payload.get("role")
        if not subject or not email or not role:
            raise TokenError("Invalid token")

        user = await self.repository.get_by_email(email)
        if user is None or str(user.id) != str(subject):
            raise InvalidCredentials("User not found")

        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value},
            secret_key=self.settings.jwt_secret,
            algorithm=self.settings.jwt_algorithm,
            expires_delta_minutes=self.settings.access_token_expire_minutes,
        )
        return TokenResponse(access_token=access_token, refresh_token=payload.refresh_token)

    async def verify_otp(self, current_user: User, payload: VerifyOtpRequest) -> VerifyOtpResponse:
        if payload.otp_code != self.settings.otp_code:
            raise InvalidOtp("Invalid OTP code")
        return VerifyOtpResponse(verified=True, message=f"OTP verified for {current_user.email}")

    async def logout(self, payload: LogoutRequest) -> MessageResponse:
        decode_refresh_token(
            token=payload.refresh_token,
            secret_key=self.settings.jwt_secret,
            algorithm=self.settings.jwt_algorithm,
        )
        return MessageResponse(message="Logout successful")
