from __future__ import annotations

from typing import AsyncIterator

import asyncpg
from fastapi import Request


async def get_db(request: Request) -> AsyncIterator[asyncpg.Connection]:
    pool = getattr(request.app.state, "db_pool", None)
    if pool is None:
        raise RuntimeError("Database pool is not initialized")

    async with pool.acquire() as connection:
        yield connection
