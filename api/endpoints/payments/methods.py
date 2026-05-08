from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from exception.payment_exceptions import raise_payment_http_exception
from schemas.payments.methods import PaymentMethodRequest, PaymentMethodResponse
from services.payments.base import PaymentServiceBase

from .dependencies import get_current_user_id, get_payment_create_service

router = APIRouter()


@router.post(
    "/methods",
    response_model=PaymentMethodResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new payment method",
)
async def add_payment_method(
    payload: PaymentMethodRequest,
    user_id: UUID = Depends(get_current_user_id),
    service: PaymentServiceBase = Depends(get_payment_create_service),
) -> PaymentMethodResponse:
    """
    Add a new payment method for the current user.
    Note: Full implementation would require a payment_methods table in the database.
    This is a placeholder for the payment methods endpoint structure.
    """
    try:
        # Placeholder - actual implementation would create a payment method record
        # and return PaymentMethodResponse
        return {
            "id": UUID("00000000-0000-0000-0000-000000000000"),
            "user_id": user_id,
            "method_type": payload.method_type,
            "is_default": payload.is_default,
            "created_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            "updated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        }
    except Exception as exc:
        raise_payment_http_exception(exc)
