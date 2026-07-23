"""
Cache service - abstraction for caching operations
"""
from typing import Any, Optional

import structlog

from src.infrastructure.cache.redis_client import RedisClient
from src.infrastructure.observability.metrics import cache_hits_total, cache_misses_total

logger = structlog.get_logger(__name__)


class CacheService:
    """Cache service for application-level caching"""

    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client

    async def get_product(self, product_id: str) -> Optional[dict]:
        """Get product from cache"""
        key = f"product:{product_id}"
        data = await self.redis_client.get_json(key)

        if data:
            cache_hits_total.labels(cache_key="product").inc()
            logger.debug("Cache hit", key=key)
        else:
            cache_misses_total.labels(cache_key="product").inc()
            logger.debug("Cache miss", key=key)

        return data

    async def set_product(self, product_id: str, data: dict, expire: int = 300) -> bool:
        """Set product in cache (5 minutes default)"""
        key = f"product:{product_id}"
        success = await self.redis_client.set_json(key, data, expire=expire)

        if success:
            logger.debug("Product cached", key=key, expire=expire)

        return success

    async def delete_product(self, product_id: str) -> bool:
        """Delete product from cache"""
        key = f"product:{product_id}"
        success = await self.redis_client.delete(key)

        if success:
            logger.debug("Product cache deleted", key=key)

        return success

    async def get_product_list(self, cache_key: str) -> Optional[dict]:
        """Get product list from cache"""
        key = f"product_list:{cache_key}"
        data = await self.redis_client.get_json(key)

        if data:
            cache_hits_total.labels(cache_key="product_list").inc()
        else:
            cache_misses_total.labels(cache_key="product_list").inc()

        return data

    async def set_product_list(self, cache_key: str, data: dict, expire: int = 60) -> bool:
        """Set product list in cache (1 minute default)"""
        key = f"product_list:{cache_key}"
        return await self.redis_client.set_json(key, data, expire=expire)

    async def increment_rate_limit(self, identifier: str, window: int = 60) -> int:
        """
        Increment rate limit counter
        Args:
            identifier: Unique identifier (e.g., IP address, user ID)
            window: Time window in seconds
        Returns:
            int: Current count
        """
        key = f"rate_limit:{identifier}"
        count = await self.redis_client.increment(key)

        if count == 1:
            # Set expiration on first increment
            await self.redis_client.expire(key, window)

        return count

    async def clear_cache_pattern(self, pattern: str) -> bool:
        """Clear cache by pattern (use cautiously)"""
        # This would require SCAN command in Redis
        # Implementation depends on specific requirements
        logger.warning("Clear cache pattern called", pattern=pattern)
        return True
