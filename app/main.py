from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import get_settings
from api.router import api_router
from db.connection import close_pool, create_pool

API_PREFIX = "/api"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    pool = await create_pool(
        database_url=settings.database_url,
        min_size=settings.db_pool_min_size,
        max_size=settings.db_pool_max_size,
    )
    app.state.db_pool = pool
    app.state.settings = settings
    try:
        yield
    finally:
        await close_pool(pool)


app = FastAPI(title="Ride Booking Backend", lifespan=lifespan)
app.include_router(api_router, prefix=API_PREFIX)
