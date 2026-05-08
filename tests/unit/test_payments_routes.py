from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.endpoints.payments import router as payments_router
from api.endpoints.payments.dependencies import (
    get_current_user_id,
    get_payment_confirm_service,
    get_payment_create_service,
    get_payment_history_service,
    get_payment_refund_service,
)
from core.enums import PaymentStatus
from models.payment import Payment

USER_ID = uuid4()
PAYMENT_ID = uuid4()
RIDE_ID = uuid4()


def _payment(status: PaymentStatus, transaction_id: str | None = None) -> Payment:
    now = datetime.now(timezone.utc)
    return Payment(
        id=PAYMENT_ID,
        ride_id=RIDE_ID,
        user_id=USER_ID,
        amount=Decimal("42.50"),
        status=status,
        payment_method="card",
        transaction_id=transaction_id,
        created_at=now,
        updated_at=now,
    )


class FakePaymentCreateService:
    def __init__(self, payment: Payment) -> None:
        self.payment = payment

    async def create_payment(
        self,
        ride_id: UUID,
        user_id: UUID,
        amount: Decimal,
        payment_method: str,
    ) -> Payment:
        return self.payment


class FakePaymentConfirmService:
    def __init__(self, payment: Payment) -> None:
        self.payment = payment

    async def confirm_payment(self, payment_id: UUID, transaction_id: str) -> Payment:
        return self.payment


class FakePaymentHistoryService:
    def __init__(self, payments: list[Payment]) -> None:
        self.payments = payments

    async def get_user_payment_history(
        self, user_id: UUID, limit: int = 10, offset: int = 0
    ) -> dict:
        return {
            "payments": self.payments,
            "total": len(self.payments),
            "limit": limit,
            "offset": offset,
        }


class FakePaymentRefundService:
    def __init__(self, payment: Payment) -> None:
        self.payment = payment

    async def refund_payment(self, payment_id: UUID) -> Payment:
        return self.payment


class FakePaymentStatusService:
    def __init__(self, payment: Payment) -> None:
        self.repository = self
        self._payment = payment

    async def get_payment_by_id(self, payment_id: UUID) -> Payment:
        return self._payment


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(payments_router)
    return app


def test_create_payment_route_returns_201() -> None:
    payment = _payment(PaymentStatus.pending)
    app = _make_app()
    app.dependency_overrides[get_current_user_id] = lambda: USER_ID
    app.dependency_overrides[get_payment_create_service] = lambda: FakePaymentCreateService(payment)

    with TestClient(app) as client:
        response = client.post(
            "/payments/create",
            json={
                "ride_id": str(RIDE_ID),
                "amount": "42.50",
                "payment_method": "card",
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["id"] == str(PAYMENT_ID)
    assert response.json()["status"] == PaymentStatus.pending.value


def test_get_payment_status_route_returns_payment() -> None:
    payment = _payment(PaymentStatus.pending)
    app = _make_app()
    app.dependency_overrides[get_current_user_id] = lambda: USER_ID
    app.dependency_overrides[get_payment_create_service] = lambda: FakePaymentStatusService(payment)

    with TestClient(app) as client:
        response = client.get(f"/payments/{PAYMENT_ID}")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["id"] == str(PAYMENT_ID)
    assert response.json()["status"] == PaymentStatus.pending.value


def test_payment_history_route_returns_paginated_results() -> None:
    payment = _payment(PaymentStatus.completed)
    app = _make_app()
    app.dependency_overrides[get_current_user_id] = lambda: USER_ID
    app.dependency_overrides[get_payment_history_service] = lambda: FakePaymentHistoryService([payment])

    with TestClient(app) as client:
        response = client.get("/payments/history", params={"page": 1, "page_size": 10})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["payments"][0]["id"] == str(PAYMENT_ID)


def test_confirm_payment_route_returns_completed_payment() -> None:
    payment = _payment(PaymentStatus.completed, transaction_id="tx_123")
    app = _make_app()
    app.dependency_overrides[get_current_user_id] = lambda: USER_ID
    app.dependency_overrides[get_payment_confirm_service] = lambda: FakePaymentConfirmService(payment)

    with TestClient(app) as client:
        response = client.post(
            f"/payments/{PAYMENT_ID}/confirm",
            json={"transaction_id": "tx_123"},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == PaymentStatus.completed.value
    assert response.json()["transaction_id"] == "tx_123"


def test_refund_payment_route_returns_refunded_payment() -> None:
    payment = _payment(PaymentStatus.refunded, transaction_id="tx_123")
    app = _make_app()
    app.dependency_overrides[get_current_user_id] = lambda: USER_ID
    app.dependency_overrides[get_payment_refund_service] = lambda: FakePaymentRefundService(payment)

    with TestClient(app) as client:
        response = client.post(
            f"/payments/{PAYMENT_ID}/refund",
            json={"reason": "customer requested refund"},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == PaymentStatus.refunded.value
