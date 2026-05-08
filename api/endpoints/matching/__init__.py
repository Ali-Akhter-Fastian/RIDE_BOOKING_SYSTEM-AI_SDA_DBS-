from __future__ import annotations

from fastapi import APIRouter

from .accept import router as accept_router
from .find import router as find_router

router = APIRouter(prefix="/matching", tags=["matching"])
router.include_router(find_router)
router.include_router(accept_router)
