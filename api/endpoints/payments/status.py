from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from exception.payment_exceptions import raise_payment_http_exception
from schemas.payments.status import PaymentStatusResponse
from services.payments.base import PaymentServiceBase

from .dependencies import get_current_user_id, get_payment_create_service

router = APIRouter()


@router.get(
    "/{payment_id}",
    response_model=PaymentStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get payment status by ID",
)
async def get_payment_status(
    payment_id: UUID,
    _user_id: UUID = Depends(get_current_user_id),
    service: PaymentServiceBase = Depends(get_payment_create_service),
) -> PaymentStatusResponse:
    try:
        payment = await service.repository.get_payment_by_id(payment_id)
        return PaymentStatusResponse.model_validate(payment)
    except Exception as exc:
        raise_payment_http_exception(exc)
