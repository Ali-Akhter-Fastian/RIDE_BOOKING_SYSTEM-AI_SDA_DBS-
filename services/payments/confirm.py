from __future__ import annotations

from uuid import UUID

from core.enums import PaymentStatus
from exception.payment_exceptions import InvalidPaymentStatus, PaymentNotFound
from services.payments.base import PaymentServiceBase


class PaymentConfirmService(PaymentServiceBase):
    """Service for confirming payments"""

    async def confirm_payment(self, payment_id: UUID, transaction_id: str):
        """Confirm a payment and update transaction ID"""
        # Get existing payment
        payment = await self.repository.get_payment_by_id(payment_id)
        
        # Validate payment status
        if payment.status != PaymentStatus.pending:
            raise InvalidPaymentStatus(
                f"Cannot confirm payment with status {payment.status}"
            )
        
        # Update transaction ID
        await self.repository.update_transaction_id(payment_id, transaction_id)
        
        # Update status to completed
        payment = await self.repository.update_payment_status(
            payment_id, PaymentStatus.completed.value
        )
        
        return payment
