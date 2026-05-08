from __future__ import annotations

from fastapi import APIRouter

from .confirm_payment import router as confirm_router
from .create_payment import router as create_router
from .history import router as history_router
from .methods import router as methods_router
from .refund import router as refund_router
from .status import router as status_router
from .webhook import router as webhook_router

# history MUST be registered before /{payment_id} — FastAPI matches in order,
# and "history" would otherwise be swallowed as a UUID path parameter.
router = APIRouter(prefix="/payments", tags=["payments"])
router.include_router(history_router)
router.include_router(webhook_router)
router.include_router(create_router)
router.include_router(confirm_router)
router.include_router(status_router)
router.include_router(refund_router)
router.include_router(methods_router)
