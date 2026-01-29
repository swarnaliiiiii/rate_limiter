import time
from app.storage.redis_client import get_redis


async def get_count(key: str, window_seconds: int) -> int:
    """
    Count requests in the last window using sorted set timestamps.
    """
    now = int(time.time())
    window_start = now - window_seconds

    redis_key = f"req:{key}"
    await get_redis().zremrangebyscore(redis_key, 0, window_start)
    return await get_redis().zcard(redis_key)