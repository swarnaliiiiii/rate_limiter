import time
from typing import Dict, List


class SlidingWindowLimiter:
    """
    In-memory sliding window rate limiter using a ring buffer.
    """

    def __init__(self, window_size: int, limit: int):
        self.window_size = window_size       
        self.limit = limit                    
        self.buckets: Dict[str, List[dict]] = {}
        # key -> list of { "ts": int, "count": int }

    def _get_buckets(self, key: str) -> List[dict]:
        if key not in self.buckets:
            self.buckets[key] = [
                {"ts": 0, "count": 0}
                for _ in range(self.window_size)
            ]
        return self.buckets[key]

    def allow(self, key: str, now: int | None = None) -> tuple[bool, int]:
        """
        Returns (allowed, current_count)
        """
        now = now or int(time.time())
        buckets = self._get_buckets(key)

        index = now % self.window_size
        bucket = buckets[index]

        # Reset bucket if it's from an old timestamp
        if bucket["ts"] != now:
            bucket["ts"] = now
            bucket["count"] = 0

        bucket["count"] += 1

        # Compute total count in sliding window
        total = 0
        for b in buckets:
            if now - b["ts"] < self.window_size:
                total += b["count"]

        allowed = total <= self.limit
        return allowed, total
