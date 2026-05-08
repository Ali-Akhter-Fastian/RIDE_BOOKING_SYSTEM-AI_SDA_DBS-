from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from services.payments.base import PaymentServiceBase


class PaymentCreateService(PaymentServiceBase):
    """Service for creating payments"""

    async def create_payment(
        self,
        ride_id: UUID,
        user_id: UUID,
        amount: Decimal,
        payment_method: str,
    ):
        """Create a new payment"""
        from uuid import uuid4
        from core.enums import PaymentStatus
        
        payment_id = uuid4()
        payment = await self.repository.create_payment(
            payment_id=payment_id,
            ride_id=ride_id,
            user_id=user_id,
            amount=amount,
            status=PaymentStatus.pending.value,
            payment_method=payment_method,
            transaction_id=None,
        )
        
        return payment
