from typing import Annotated
from fastapi import Depends
from app.shared.dependencies import RedisClient
from redis.asyncio import Redis
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID
import json


class TokenRepository:

    BLACKLIST_PREFIX = "token:blacklist:"

    def __init__(self, redis: Redis):
        self.redis = redis

    async def blacklist_token(self, jti: str, expires_at: datetime) -> bool:
        """
        Thêm token vào blacklist với TTL tự động expire.

        Args:
            jti: JWT ID của token cần blacklist
            expires_at: Thời gian hết hạn của token

        Returns:
            bool: True nếu blacklist thành công
        """
        key = f"{self.BLACKLIST_PREFIX}{jti}"

        ttl = int((expires_at - datetime.now(timezone.utc)).total_seconds())

        if ttl > 0:
            await self.redis.setex(key, ttl, "revoked")
            return True

        return False  # Token đã hết hạn

    async def is_blacklisted(self, jti: str) -> bool:
        """
        Kiểm tra token có trong blacklist không.

        Args:
            jti: JWT ID của token cần kiểm tra

        Returns:
            bool: True nếu token trong blacklist
        """
        key = f"{self.BLACKLIST_PREFIX}{jti}"

        return await self.redis.exists(key) > 0


async def get_token_repository(redis_client: RedisClient) -> TokenRepository:
    return TokenRepository(redis_client)

TokenRepoDep = Annotated[TokenRepository, Depends(get_token_repository)]
