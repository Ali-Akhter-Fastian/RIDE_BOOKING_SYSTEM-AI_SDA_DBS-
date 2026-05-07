from __future__ import annotations

from fastapi import APIRouter

from api.endpoints.rides import router as rides_router

api_router = APIRouter()
api_router.include_router(rides_router)
from api.endpoints.auth import router as auth_router

api_router = APIRouter()
api_router.include_router(auth_router)
