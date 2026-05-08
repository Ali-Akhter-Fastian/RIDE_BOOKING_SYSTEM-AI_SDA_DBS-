from __future__ import annotations

from fastapi import APIRouter

from api.endpoints.auth import router as auth_router
from api.endpoints.matching import router as matching_router
from api.endpoints.rides import router as rides_router

api_router = APIRouter()
api_router.include_router(rides_router)
api_router.include_router(matching_router)
api_router.include_router(auth_router)
