from typing import Tuple

import aioredis
import backoff
from fastapi_cache.backends.redis import RedisBackend as BaseRedisBackend
from fastapi_cache import FastAPICache
from core.config import REDIS_HOST, REDIS_PORT


class RedisBackend(BaseRedisBackend):

    @backoff.on_exception(backoff.expo, OSError, max_tries=10)
    async def get_with_ttl(self, key: str) -> Tuple[int, str]:
        return await super().get_with_ttl(key)

    @backoff.on_exception(backoff.expo, OSError, max_tries=10)
    async def set(self, key: str, value: str, expire: int = None):
        return await super().set(key, value, expire=expire)

    @backoff.on_exception(backoff.expo, OSError, max_tries=10)
    async def get(self, key) -> str:
        return await super().get(key)


@backoff.on_exception(backoff.expo, OSError, max_tries=10)
async def create_redis_connection():
    pool = await aioredis.create_redis_pool((REDIS_HOST, REDIS_PORT), minsize=10, maxsize=20)
    FastAPICache.init(RedisBackend(pool))


async def close_redis_connection():
    redis_backend: RedisBackend = FastAPICache().get_backend()
    redis_backend.redis.close()
    await redis_backend.redis.wait_closed()


on_startup = create_redis_connection
on_shutdown = close_redis_connection
