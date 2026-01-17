import time
import json
from app.storage.redis_client import get_redis


class RedisSlidingWindowLimiter:
    def __init__(self, window_size: int, limit: int):
        self.window_size = window_size
        self.limit = limit

    def _key(self, scope: str) -> str:
        return f"rate:{scope}"

    def allow(self, scope: str, now: int | None = None) -> tuple[bool, int]:
        now = now or int(time.time())
        key = self._key(scope)

        data = get_redis.get(key)
        if data is None:
            buckets = [{"ts": 0, "count": 0} for _ in range(self.window_size)]
        else:
            buckets = json.loads(data)

        idx = now % self.window_size
        bucket = buckets[idx]

        if bucket["ts"] != now:
            bucket["ts"] = now
            bucket["count"] = 0

        bucket["count"] += 1

        total = 0
        for b in buckets:
            if now - b["ts"] < self.window_size:
                total += b["count"]

        get_redis.setex(
            key,
            self.window_size + 5,
            json.dumps(buckets)
        )

        return total <= self.limit, total
