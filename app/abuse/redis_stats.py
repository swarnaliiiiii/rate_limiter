import time
from app.storage.redis_client import get_redis


def _key(key: str) -> str:
    return f"req:{key}"


async def record_event(key: str, now: int | None = None) -> None:
    """
    Record a single request occurrence in the sorted set used for
    baseline / spike analysis. Without this, get_count() always reads 0.
    """
    now = now or int(time.time())
    redis_key = _key(key)
    # Unique member per call so same-second events don't collapse.
    await get_redis().zadd(redis_key, {f"{now}-{time.time_ns()}": now})
    # Keep the set bounded to the longest window any detector cares about.
    await get_redis().expire(redis_key, 600)


async def get_count(key: str, window_seconds: int) -> int:
    """
    Count requests in the last window using sorted set timestamps.
    """
    now = int(time.time())
    window_start = now - window_seconds

    redis_key = _key(key)
    await get_redis().zremrangebyscore(redis_key, 0, window_start)
    return await get_redis().zcount(redis_key, window_start, now)
