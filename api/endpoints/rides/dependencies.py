from __future__ import annotations

from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings, get_settings
from app.dependencies import get_db
from core.enums import UserRole
from core.security import decode_access_token
from exception.auth_exceptions import TokenError
from exception.ride_exceptions import raise_ride_http_exception
from repositories.n8n_workflow_log_repository import N8nWorkflowLogRepository
from repositories.ride_repository import RideRepository
from services.rides import (
    DriverRatingService,
    RideCreationService,
    RideHistoryService,
    RideLifecycleService,
    RideMatchingService,
)
from services.rides.ranking import LocalRankingProvider, N8nRankingProvider, RankingProvider

bearer_scheme = HTTPBearer(auto_error=True)


# ------------------------------------------------------------------ #
# Token helpers                                                        #
# ------------------------------------------------------------------ #

def get_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    return credentials.credentials


def _decode_token(token: str, settings: Settings) -> dict:
    return decode_access_token(
        token=token,
        secret_key=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def _extract_uuid(payload: dict) -> UUID:
    sub = payload.get("sub")
    if not sub:
        raise TokenError("Invalid token subject")
    try:
        return UUID(str(sub))
    except ValueError as exc:
        raise TokenError("Token subject is not a valid UUID") from exc


# ------------------------------------------------------------------ #
# Current-user extractors (role-enforced)                             #
# ------------------------------------------------------------------ #

def get_current_rider_id(
    token: str = Depends(get_bearer_token),#Instead, it says: “call the function inside Depends(...) and use its return value here.”
    settings: Settings = Depends(get_settings),
) -> UUID:
    """Decode the JWT and assert the caller is a rider."""
    try:
        payload = _decode_token(token, settings)
        if payload.get("role") != UserRole.rider.value:
            raise TokenError("Only riders can perform this action")
        return _extract_uuid(payload)
    except Exception as exc:
        raise_ride_http_exception(exc)


def get_current_driver_id(
    token: str = Depends(get_bearer_token),
    settings: Settings = Depends(get_settings),
) -> UUID:
    """Decode the JWT and assert the caller is a driver."""
    try:
        payload = _decode_token(token, settings)
        if payload.get("role") != UserRole.driver.value:
            raise TokenError("Only drivers can perform this action")
        return _extract_uuid(payload)
    except Exception as exc:
        raise_ride_http_exception(exc)


def get_current_user_id(
    token: str = Depends(get_bearer_token),
    settings: Settings = Depends(get_settings),
) -> UUID:
    """Decode the JWT without role enforcement — any authenticated user."""
    try:
        payload = _decode_token(token, settings)
        return _extract_uuid(payload)
    except Exception as exc:
        raise_ride_http_exception(exc)


def get_current_user_role(
    token: str = Depends(get_bearer_token),
    settings: Settings = Depends(get_settings),
) -> UserRole:
    try:
        payload = _decode_token(token, settings)
        role = payload.get("role")
        if role not in (UserRole.rider.value, UserRole.driver.value):
            raise TokenError("Invalid role in token")
        return UserRole(role)
    except Exception as exc:
        raise_ride_http_exception(exc)


# ------------------------------------------------------------------ #
# Service factories                                                    #
# ------------------------------------------------------------------ #

def get_ride_creation_service(
    connection=Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> RideCreationService:
    return RideCreationService(RideRepository(connection), settings)


def get_ride_lifecycle_service(
    connection=Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> RideLifecycleService:
    return RideLifecycleService(RideRepository(connection), settings)


def get_ride_history_service(
    connection=Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> RideHistoryService:
    return RideHistoryService(RideRepository(connection), settings)


def get_driver_rating_service(
    connection=Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> DriverRatingService:
    return DriverRatingService(RideRepository(connection), settings)


def get_ride_matching_service(
    connection=Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> RideMatchingService:
    ranking_provider: RankingProvider
    local_provider = LocalRankingProvider()

    if settings.ranking_provider == "n8n" and settings.n8n_ranking_webhook_url:
        fallback_provider = local_provider if settings.n8n_ranking_fallback_enabled else None
        ranking_provider = N8nRankingProvider(
            webhook_url=settings.n8n_ranking_webhook_url,
            timeout_seconds=settings.n8n_ranking_timeout_seconds,
            fallback_provider=fallback_provider,
            auth_header=settings.n8n_ranking_auth_header,
            workflow_log_repository=N8nWorkflowLogRepository(connection),
        )
    else:
        ranking_provider = local_provider

    return RideMatchingService(
        RideRepository(connection),
        settings,
        ranking_provider=ranking_provider,
    )
