from __future__ import annotations

from app.config import Settings
from repositories.payment_repository import PaymentRepository


class PaymentServiceBase:
    def __init__(self, repository: PaymentRepository, settings: Settings) -> None:
        self.repository = repository
        self.settings = settings
