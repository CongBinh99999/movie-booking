import redis.asyncio as redis
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from app.core.config import get_setting


setting = get_setting()


redis_pool = redis.ConnectionPool.from_url(setting.REDIS_URL)


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    async with redis.Redis(connection_pool=redis_pool) as client:
        yield client


@asynccontextmanager
async def get_redis_client() -> AsyncGenerator[redis.Redis, None]:
    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        await client.aclose()
