import redis
import time
from app.storage.redis_client import redis_client

def get_count(key: str, window_seconds: int) -> int:
    """
    Count requests in the last window using sorted set timestamps.
    """
    now = int(time.time())
    window_start = now - window_seconds

    redis_key = f"req:{key}"
    redis_client.zremrangebyscore(redis_key, 0, window_start)
    return redis_client.zcard(redis_key)
