"""Redis client for OTP and cache storage."""

import redis.asyncio as aioredis
from typing import Optional
from .config import settings


class RedisClient:
    """Async Redis client wrapper."""

    def __init__(self):
        self._pool: Optional[aioredis.ConnectionPool] = None
        self._client: Optional[aioredis.Redis] = None

    async def connect(self):
        """Create Redis connection pool."""
        if self._pool is None:
            self._pool = aioredis.ConnectionPool.from_url(
                settings.redis_url,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True
            )
            self._client = aioredis.Redis(connection_pool=self._pool)

    async def disconnect(self):
        """Close Redis connection pool."""
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
            self._client = None

    @property
    def client(self) -> aioredis.Redis:
        """Get Redis client (call connect() first)."""
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        return self._client

    async def set_with_ttl(self, key: str, value: str, ttl_seconds: int) -> bool:
        """Set a key with expiration time."""
        return await self.client.setex(key, ttl_seconds, value)

    async def get(self, key: str) -> Optional[str]:
        """Get a value by key."""
        return await self.client.get(key)

    async def delete(self, key: str) -> int:
        """Delete a key."""
        return await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        return await self.client.exists(key) > 0


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """Dependency to get Redis client."""
    if redis_client._client is None:
        await redis_client.connect()
    return redis_client
