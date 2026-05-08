from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from exception.payment_exceptions import raise_payment_http_exception
from schemas.payments.confirm import ConfirmPaymentRequest, ConfirmPaymentResponse
from services.payments.confirm import PaymentConfirmService

from .dependencies import get_current_user_id, get_payment_confirm_service

router = APIRouter()


@router.post(
    "/{payment_id}/confirm",
    response_model=ConfirmPaymentResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm a payment with transaction ID",
)
async def confirm_payment(
    payment_id: UUID,
    payload: ConfirmPaymentRequest,
    _user_id: UUID = Depends(get_current_user_id),
    service: PaymentConfirmService = Depends(get_payment_confirm_service),
) -> ConfirmPaymentResponse:
    try:
        payment = await service.confirm_payment(
            payment_id=payment_id,
            transaction_id=payload.transaction_id,
        )
        return ConfirmPaymentResponse.model_validate(payment)
    except Exception as exc:
        raise_payment_http_exception(exc)
