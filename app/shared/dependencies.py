from app.shared.database import get_db
from app.shared.redis import get_redis
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis


DbSession = Annotated[AsyncSession, Depends(get_db)]
RedisClient = Annotated[redis.Redis, Depends(get_redis)]
