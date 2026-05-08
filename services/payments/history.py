from __future__ import annotations

from uuid import UUID

from services.payments.base import PaymentServiceBase


class PaymentHistoryService(PaymentServiceBase):
    """Service for retrieving payment history"""

    async def get_user_payment_history(self, user_id: UUID, limit: int = 10, offset: int = 0):
        """Get payment history for a user"""
        payments = await self.repository.get_payments_paginated(user_id, limit, offset)
        total = await self.repository.count_payments_by_user(user_id)
        
        return {
            "payments": payments,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    async def get_payment_by_ride(self, ride_id: UUID):
        """Get payment information for a ride"""
        return await self.repository.get_payment_by_ride_id(ride_id)
