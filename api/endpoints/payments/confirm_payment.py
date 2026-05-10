from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from core.ws import ws_hub
from exception.payment_exceptions import raise_payment_http_exception
from schemas.payments.confirm import (
    ConfirmPaymentByPathRequest,
    ConfirmPaymentRequest,
    ConfirmPaymentResponse,
)
from services.payments.confirm import PaymentConfirmService

from .dependencies import get_current_user_id, get_payment_confirm_service

router = APIRouter()


@router.post(
    "/confirm",
    response_model=ConfirmPaymentResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm a payment",
)
async def confirm_payment(
    payload: ConfirmPaymentRequest,
    user_id: UUID = Depends(get_current_user_id),
    service: PaymentConfirmService = Depends(get_payment_confirm_service),
) -> ConfirmPaymentResponse:
    try:
        payment = await service.confirm_payment(
            payment_id=payload.payment_id,
            user_id=user_id,
            transaction_id=payload.transaction_id,
        )
        await ws_hub.emit_to_rider(
            payment.user_id,
            "payment_done",
            {
                "payment_id": str(payment.id),
                "ride_id": str(payment.ride_id),
                "status": payment.status.value,
                "amount": str(payment.amount),
            },
        )
        return ConfirmPaymentResponse.model_validate(payment)
    except Exception as exc:
        raise_payment_http_exception(exc)


@router.post(
    "/{payment_id}/confirm",
    response_model=ConfirmPaymentResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm a payment with transaction ID (legacy path)",
)
async def confirm_payment_legacy(
    payment_id: UUID,
    payload: ConfirmPaymentByPathRequest,
    user_id: UUID = Depends(get_current_user_id),
    service: PaymentConfirmService = Depends(get_payment_confirm_service),
) -> ConfirmPaymentResponse:
    try:
        payment = await service.confirm_payment(
            payment_id=payment_id,
            user_id=user_id,
            transaction_id=payload.transaction_id,
        )
        await ws_hub.emit_to_rider(
            payment.user_id,
            "payment_done",
            {
                "payment_id": str(payment.id),
                "ride_id": str(payment.ride_id),
                "status": payment.status.value,
                "amount": str(payment.amount),
            },
        )
        return ConfirmPaymentResponse.model_validate(payment)
    except Exception as exc:
        raise_payment_http_exception(exc)
