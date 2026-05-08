from __future__ import annotations

from fastapi import APIRouter, Depends, status

from exception.payment_exceptions import raise_payment_http_exception
from services.payments.webhook import PaymentWebhookService

from .dependencies import get_payment_webhook_service

router = APIRouter()


@router.post(
    "/webhook/payment-gateway",
    status_code=status.HTTP_200_OK,
    summary="Handle payment gateway webhook",
)
async def handle_payment_webhook(
    webhook_data: dict,
    service: PaymentWebhookService = Depends(get_payment_webhook_service),
):
    try:
        # Verify webhook signature first
        # signature = request.headers.get("X-Signature")
        # if not await service.verify_webhook_signature(str(webhook_data), signature):
        #     raise PaymentWebhookError("Invalid webhook signature")
        
        updated_payment = await service.handle_payment_webhook(webhook_data)
        return {"status": "success", "payment_id": str(updated_payment.id)}
    except Exception as exc:
        raise_payment_http_exception(exc)
