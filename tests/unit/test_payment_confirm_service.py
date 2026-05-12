from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from app.config import Settings
from core.enums import PaymentStatus
from models.payment import Payment
from services.payments.confirm import PaymentConfirmService


def _make_payment(
    *,
    payment_id: UUID,
    ride_id: UUID,
    user_id: UUID,
    status: PaymentStatus,
    transaction_id: str | None,
) -> Payment:
    now = datetime.now(timezone.utc)
    return Payment(
        id=payment_id,
        ride_id=ride_id,
        user_id=user_id,
        amount=Decimal("4.20"),
        status=status,
        payment_method="cash",
        transaction_id=transaction_id,
        deleted_at=None,
        created_at=now,
        updated_at=now,
    )


@dataclass
class FakeConnection:
    executed: list[tuple[str, tuple[object, ...]]] = field(default_factory=list)

    async def execute(self, sql: str, *args: object) -> str:
        self.executed.append((sql, args))
        return "UPDATE 1"


@dataclass
class FakePaymentRepository:
    connection: FakeConnection
    payment: Payment

    async def get_payment_by_id(self, payment_id: UUID) -> Payment:
        return self.payment

    async def update_transaction_id(self, payment_id: UUID, transaction_id: str) -> Payment:
        self.payment = _make_payment(
            payment_id=self.payment.id,
            ride_id=self.payment.ride_id,
            user_id=self.payment.user_id,
            status=self.payment.status,
            transaction_id=transaction_id,
        )
        return self.payment

    async def update_payment_status(self, payment_id: UUID, status: str) -> Payment:
        self.payment = _make_payment(
            payment_id=self.payment.id,
            ride_id=self.payment.ride_id,
            user_id=self.payment.user_id,
            status=PaymentStatus(status),
            transaction_id=self.payment.transaction_id,
        )
        return self.payment


@pytest.fixture()
def settings() -> Settings:
    return Settings(
        database_url="postgresql://localhost/test",
        jwt_secret="test-secret",
        jwt_algorithm="HS256",
        access_token_expire_minutes=60,
        refresh_token_expire_minutes=10080,
    )


@pytest.mark.asyncio()
async def test_confirm_payment_updates_ride_and_driver_earnings(settings: Settings) -> None:
    connection = FakeConnection()
    payment_id = uuid4()
    ride_id = uuid4()
    user_id = uuid4()
    payment = _make_payment(
        payment_id=payment_id,
        ride_id=ride_id,
        user_id=user_id,
        status=PaymentStatus.pending,
        transaction_id=None,
    )
    repo = FakePaymentRepository(connection=connection, payment=payment)

    result = await PaymentConfirmService(repo, settings).confirm_payment(payment_id, user_id)

    assert result.status == PaymentStatus.completed
    assert len(connection.executed) == 2
    assert "UPDATE rides SET status = 'completed'" in connection.executed[0][0]
    assert connection.executed[0][1] == (str(ride_id),)
    assert "SET total_earnings" in connection.executed[1][0]
    assert connection.executed[1][1] == (str(ride_id), float(payment.amount))
