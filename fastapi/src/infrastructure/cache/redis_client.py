"""
Redis client for caching
"""
import json
from functools import lru_cache
from typing import Any, Optional

import structlog
from redis import asyncio as aioredis

from src.config.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class RedisClient:
    """Redis client wrapper for caching operations"""

    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        """Connect to Redis"""
        try:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=settings.REDIS_DECODE_RESPONSES,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
            )
            await self.redis.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error("Redis connection failed", error=str(e))
            self.redis = None

    async def close(self) -> None:
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")

    async def ping(self) -> bool:
        """Ping Redis to check connection"""
        if not self.redis:
            await self.connect()

        try:
            return await self.redis.ping()
        except Exception as e:
            logger.error("Redis ping failed", error=str(e))
            return False

    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        if not self.redis:
            return None

        try:
            value = await self.redis.get(key)
            logger.debug("Cache GET", key=key, hit=value is not None)
            return value
        except Exception as e:
            logger.error("Redis GET error", key=key, error=str(e))
            return None

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """
        Set key-value pair
        Args:
            key: Cache key
            value: Cache value
            expire: Expiration time in seconds
        """
        if not self.redis:
            return False

        try:
            await self.redis.set(key, value, ex=expire)
            logger.debug("Cache SET", key=key, expire=expire)
            return True
        except Exception as e:
            logger.error("Redis SET error", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete key"""
        if not self.redis:
            return False

        try:
            await self.redis.delete(key)
            logger.debug("Cache DELETE", key=key)
            return True
        except Exception as e:
            logger.error("Redis DELETE error", key=key, error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.redis:
            return False

        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error("Redis EXISTS error", key=key, error=str(e))
            return False

    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value by key"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                logger.error("JSON decode error", key=key, error=str(e))
        return None

    async def set_json(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set JSON value"""
        try:
            json_value = json.dumps(value)
            return await self.set(key, json_value, expire)
        except (TypeError, ValueError) as e:
            logger.error("JSON encode error", key=key, error=str(e))
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter"""
        if not self.redis:
            return None

        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error("Redis INCRBY error", key=key, error=str(e))
            return None

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key"""
        if not self.redis:
            return False

        try:
            return await self.redis.expire(key, seconds)
        except Exception as e:
            logger.error("Redis EXPIRE error", key=key, error=str(e))
            return False


# Singleton instance
_redis_client: Optional[RedisClient] = None


@lru_cache()
def get_redis_client() -> RedisClient:
    """Get Redis client singleton"""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client
