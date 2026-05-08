from __future__ import annotations

from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, status

from exception.payment_exceptions import raise_payment_http_exception
from schemas.payments.create import CreatePaymentRequest, CreatePaymentResponse
from services.payments.create import PaymentCreateService

from .dependencies import get_current_user_id, get_payment_create_service

router = APIRouter()


@router.post(
    "/create",
    response_model=CreatePaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new payment",
)
async def create_payment(
    payload: CreatePaymentRequest,
    user_id: UUID = Depends(get_current_user_id),
    service: PaymentCreateService = Depends(get_payment_create_service),
) -> CreatePaymentResponse:
    try:
        payment = await service.create_payment(
            ride_id=payload.ride_id,
            user_id=user_id,
            amount=payload.amount,
            payment_method=payload.payment_method,
        )
        return CreatePaymentResponse.model_validate(payment)
    except Exception as exc:
        raise_payment_http_exception(exc)
