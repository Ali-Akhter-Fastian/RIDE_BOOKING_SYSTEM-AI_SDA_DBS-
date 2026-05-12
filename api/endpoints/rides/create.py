from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from exception.ride_exceptions import raise_ride_http_exception
from schemas.rides.create import CreateRideRequest, CreateRideResponse
from services.rides import RideCreationService

from .dependencies import get_current_rider_id, get_ride_creation_service

router = APIRouter()


@router.post(
    "/create",
    response_model=CreateRideResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Request a new ride",
)
async def create_ride(
    payload: CreateRideRequest,
    rider_id: UUID = Depends(get_current_rider_id),
    service: RideCreationService = Depends(get_ride_creation_service),
) -> CreateRideResponse:
    try:
        ride = await service.create_ride(payload, rider_id)
        return CreateRideResponse.model_validate(ride)
    except Exception as exc:
        raise_ride_http_exception(exc)
