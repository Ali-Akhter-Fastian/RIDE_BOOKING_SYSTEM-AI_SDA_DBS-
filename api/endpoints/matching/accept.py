from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from api.endpoints.rides.dependencies import (
    get_current_driver_id,
    get_ride_matching_service,
)
from exception.ride_exceptions import raise_ride_http_exception
from schemas.matching.accept import MatchingAcceptRequest
from schemas.rides.get import RideDetailResponse
from services.rides.matching import RideMatchingService

router = APIRouter()


@router.post(
    "/accept",
    response_model=RideDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Driver accepts a matched ride offer",
)
async def accept_matched_ride(
    payload: MatchingAcceptRequest,
    driver_id: UUID = Depends(get_current_driver_id),
    service: RideMatchingService = Depends(get_ride_matching_service),
) -> RideDetailResponse:
    try:
        ride = await service.driver_accept_matched_ride(payload.ride_id, driver_id)
        return RideDetailResponse.model_validate(ride)
    except Exception as exc:
        raise_ride_http_exception(exc)
