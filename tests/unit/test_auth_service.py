from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from app.config import Settings
from core.enums import UserRole
from core.exceptions import InvalidCredentials, InvalidOtp, TokenError, UserExists
from models.user import User
from schemas.auth import LoginRequest, LogoutRequest, RefreshTokenRequest, RegisterRequest, VerifyOtpRequest
from services.auth import LoginAuthService, RegisterAuthService, SessionAuthService


@dataclass
class FakeAuthRepository:
    user_by_email: dict[str, User] | None = None

    def __post_init__(self) -> None:
        if self.user_by_email is None:
            self.user_by_email = {}

    async def get_by_email(self, email: str) -> User | None:
        return self.user_by_email.get(email.lower())

    async def get_by_id(self, user_id: UUID) -> User | None:
        for user in self.user_by_email.values():
            if user.id == user_id:
                return user
        return None

    async def create(self, user: User) -> User:
        self.user_by_email[user.email] = user
        return User(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            password_hash=user.password_hash,
            role=user.role,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )


@pytest.fixture()
def settings() -> Settings:
    return Settings(
        database_url="postgresql://localhost/test",
        jwt_secret="test-secret",
        jwt_algorithm="HS256",
        access_token_expire_minutes=30,
    )


@pytest.fixture()
def repository() -> FakeAuthRepository:
    return FakeAuthRepository()


@pytest.mark.asyncio()
async def test_register_user_hashes_password(repository: FakeAuthRepository, settings: Settings) -> None:
    service = RegisterAuthService(repository, settings)
    payload = RegisterRequest(full_name="Test Rider", email="rider@example.com", password="password123")

    user = await service.register_user(payload)

    assert user.email == "rider@example.com"
    assert user.password_hash != payload.password
    assert user.role == UserRole.rider


@pytest.mark.asyncio()
async def test_register_user_rejects_duplicates(repository: FakeAuthRepository, settings: Settings) -> None:
    service = RegisterAuthService(repository, settings)
    existing = User(
        id=uuid4(),
        full_name="Existing User",
        email="existing@example.com",
        password_hash="$2b$12$example",
        role=UserRole.rider,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    repository.user_by_email[existing.email] = existing

    payload = RegisterRequest(full_name="Existing User", email=existing.email, password="password123")

    with pytest.raises(UserExists):
        await service.register_user(payload)


@pytest.mark.asyncio()
async def test_login_user_returns_token(repository: FakeAuthRepository, settings: Settings) -> None:
    service = LoginAuthService(repository, settings)
    existing = User(
        id=uuid4(),
        full_name="Login User",
        email="login@example.com",
        password_hash="",
        role=UserRole.driver,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    from core.security import hash_password

    existing.password_hash = hash_password("password123")
    repository.user_by_email[existing.email] = existing

    token_response = await service.login_user(LoginRequest(email=existing.email, password="password123"))

    assert token_response.access_token
    assert token_response.refresh_token
    assert token_response.token_type == "bearer"


@pytest.mark.asyncio()
async def test_login_user_rejects_invalid_password(repository: FakeAuthRepository, settings: Settings) -> None:
    service = LoginAuthService(repository, settings)
    existing = User(
        id=uuid4(),
        full_name="Login User",
        email="login@example.com",
        password_hash="",
        role=UserRole.driver,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    from core.security import hash_password

    existing.password_hash = hash_password("password123")
    repository.user_by_email[existing.email] = existing

    with pytest.raises(InvalidCredentials):
        await service.login_user(LoginRequest(email=existing.email, password="wrong-password"))


@pytest.mark.asyncio()
async def test_refresh_access_token_returns_new_access_token(
    repository: FakeAuthRepository,
    settings: Settings,
) -> None:
    login_service = LoginAuthService(repository, settings)
    service = SessionAuthService(repository, settings)
    existing = User(
        id=uuid4(),
        full_name="Refresh User",
        email="refresh@example.com",
        password_hash="",
        role=UserRole.rider,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    from core.security import hash_password

    existing.password_hash = hash_password("password123")
    repository.user_by_email[existing.email] = existing

    tokens = await login_service.login_user(LoginRequest(email=existing.email, password="password123"))
    refreshed_tokens = await service.refresh_access_token(
        RefreshTokenRequest(refresh_token=tokens.refresh_token)
    )

    assert refreshed_tokens.access_token
    assert refreshed_tokens.refresh_token == tokens.refresh_token


@pytest.mark.asyncio()
async def test_refresh_access_token_rejects_non_refresh_token(
    repository: FakeAuthRepository,
    settings: Settings,
) -> None:
    service = SessionAuthService(repository, settings)

    with pytest.raises(TokenError):
        await service.refresh_access_token(RefreshTokenRequest(refresh_token="invalid-token"))


@pytest.mark.asyncio()
async def test_verify_otp_rejects_invalid_code(repository: FakeAuthRepository, settings: Settings) -> None:
    service = SessionAuthService(repository, settings)
    user = User(
        id=uuid4(),
        full_name="OTP User",
        email="otp@example.com",
        password_hash="$2b$12$example",
        role=UserRole.rider,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    with pytest.raises(InvalidOtp):
        await service.verify_otp(user, VerifyOtpRequest(otp_code="000000"))


@pytest.mark.asyncio()
async def test_logout_accepts_valid_refresh_token(
    repository: FakeAuthRepository,
    settings: Settings,
) -> None:
    login_service = LoginAuthService(repository, settings)
    service = SessionAuthService(repository, settings)
    existing = User(
        id=uuid4(),
        full_name="Logout User",
        email="logout@example.com",
        password_hash="",
        role=UserRole.driver,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    from core.security import hash_password

    existing.password_hash = hash_password("password123")
    repository.user_by_email[existing.email] = existing

    tokens = await login_service.login_user(LoginRequest(email=existing.email, password="password123"))
    response = await service.logout(LogoutRequest(refresh_token=tokens.refresh_token))

    assert response.message == "Logout successful"
