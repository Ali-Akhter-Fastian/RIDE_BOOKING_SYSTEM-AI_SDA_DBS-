from __future__ import annotations

from fastapi import APIRouter

from .register import router as register_router

router = APIRouter(prefix="/auth", tags=["auth"])
router.include_router(register_router)
