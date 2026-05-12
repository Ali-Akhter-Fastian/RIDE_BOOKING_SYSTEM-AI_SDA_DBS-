from __future__ import annotations

from uuid import UUID, uuid4

from core.enums import PaymentStatus
from exception.payment_exceptions import (
    InvalidPaymentStatus,
    PaymentOwnershipError,
)
from services.payments.base import PaymentServiceBase


class PaymentConfirmService(PaymentServiceBase):
    """Service for confirming payments"""

    async def confirm_payment(
        self,
        payment_id: UUID,
        user_id: UUID,
        transaction_id: str | None = None,
    ):
        """Confirm a pending payment with an internal transaction identifier."""
        payment = await self.repository.get_payment_by_id(payment_id)

        if str(payment.user_id) != str(user_id):
            raise PaymentOwnershipError("You are not allowed to confirm this payment")

        if payment.status == PaymentStatus.completed:
            return payment

        if payment.status not in (PaymentStatus.pending, PaymentStatus.processing):
            raise InvalidPaymentStatus(
                f"Cannot confirm payment with status {payment.status.value}"
            )

        resolved_transaction_id = transaction_id or f"INT-{uuid4().hex[:12].upper()}"
        if payment.transaction_id != resolved_transaction_id:
            await self.repository.update_transaction_id(payment_id, resolved_transaction_id)

        confirmed = await self.repository.update_payment_status(
            payment_id, PaymentStatus.completed.value
        )

        if confirmed is None:
            raise ValueError(f"Payment {payment_id} not found after status update")

        if hasattr(self.repository, "connection"):
            # First mark the ride completed to ensure earnings calculation sees the final state
            await self.repository.connection.execute(
                """
                UPDATE rides SET status = 'completed', updated_at = NOW()
                WHERE id = $1
                """,
                str(confirmed.ride_id),
            )
            # Then update the driver's total earnings based on the ride
            await self.repository.connection.execute(
                """
                UPDATE drivers d
                SET total_earnings = COALESCE(d.total_earnings, 0) + $2,
                    updated_at = NOW()
                FROM rides r
                WHERE r.id = $1
                  AND r.driver_id = d.id
                """,
                str(confirmed.ride_id),
                float(confirmed.amount),
            )
        return confirmed
