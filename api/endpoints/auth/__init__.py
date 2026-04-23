from __future__ import annotations

from fastapi import APIRouter

from .login import router as login_router
from .profile import router as profile_router
from .register import router as register_router
from .session import router as session_router

router = APIRouter(prefix="/auth", tags=["auth"])
router.include_router(register_router)
router.include_router(login_router)
router.include_router(session_router)
router.include_router(profile_router)
