from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from exception.payment_exceptions import raise_payment_http_exception
from schemas.payments.refund import RefundPaymentRequest, RefundResponse
from services.payments.refund import PaymentRefundService

from .dependencies import get_current_user_id, get_payment_refund_service

router = APIRouter()


@router.post(
    "/{payment_id}/refund",
    response_model=RefundResponse,
    status_code=status.HTTP_200_OK,
    summary="Refund a completed payment",
)
async def refund_payment(
    payment_id: UUID,
    payload: RefundPaymentRequest,
    _user_id: UUID = Depends(get_current_user_id),
    service: PaymentRefundService = Depends(get_payment_refund_service),
) -> RefundResponse:
    try:
        payment = await service.refund_payment(payment_id)
        return RefundResponse.model_validate(payment)
    except Exception as exc:
        raise_payment_http_exception(exc)
