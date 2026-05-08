from __future__ import annotations

from uuid import UUID

from core.enums import PaymentStatus
from exception.payment_exceptions import InvalidPaymentStatus, PaymentNotFound
from services.payments.base import PaymentServiceBase


class PaymentRefundService(PaymentServiceBase):
    """Service for processing refunds"""

    async def refund_payment(self, payment_id: UUID):
        """Process a refund for a payment"""
        # Get existing payment
        payment = await self.repository.get_payment_by_id(payment_id)
        
        # Validate payment status - can only refund completed payments
        if payment.status != PaymentStatus.completed:
            raise InvalidPaymentStatus(
                f"Cannot refund payment with status {payment.status}"
            )
        
        # Update status to refunded
        payment = await self.repository.update_payment_status(
            payment_id, PaymentStatus.refunded.value
        )
        
        return payment

    async def partial_refund(self, payment_id: UUID, refund_amount: float):
        """Process a partial refund"""
        payment = await self.repository.get_payment_by_id(payment_id)
        
        if payment.status != PaymentStatus.completed:
            raise InvalidPaymentStatus(
                f"Cannot refund payment with status {payment.status}"
            )
        
        # For partial refunds, update to partially_refunded
        payment = await self.repository.update_payment_status(
            payment_id, PaymentStatus.partially_refunded.value
        )
        
        return payment
