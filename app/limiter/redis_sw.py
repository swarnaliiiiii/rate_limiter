import time
from app.storage.redis_client import get_redis


# Atomic sliding-window check using a sorted set of request timestamps.
# Trimming old entries, counting, and conditionally admitting the request
# all happen inside one Lua script so concurrent callers can't race.
#
# KEYS[1] = the rate key
# ARGV[1] = now (unix seconds)
# ARGV[2] = window size (seconds)
# ARGV[3] = limit
# ARGV[4] = unique member suffix (avoids collisions within the same second)
# Returns: {allowed (1/0), current_count}
_SLIDING_WINDOW_LUA = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local member = ARGV[1] .. "-" .. ARGV[4]

redis.call("ZREMRANGEBYSCORE", key, 0, now - window)
local count = redis.call("ZCARD", key)

if count < limit then
    redis.call("ZADD", key, now, member)
    redis.call("EXPIRE", key, window + 5)
    return {1, count + 1}
end

return {0, count}
"""


class RedisSlidingWindowLimiter:
    def __init__(self, window_size: int, limit: int):
        self.window_size = window_size
        self.limit = limit

    def _key(self, scope: str) -> str:
        return f"rate:{scope}"

    async def allow(self, scope: str, now: int | None = None) -> tuple[bool, int]:
        now = now or int(time.time())
        key = self._key(scope)

        # A monotonically-unique suffix so two requests in the same second
        # don't overwrite each other as the same sorted-set member.
        suffix = time.time_ns()

        allowed, count = await get_redis().eval(
            _SLIDING_WINDOW_LUA,
            1,
            key,
            now,
            self.window_size,
            self.limit,
            suffix,
        )

        return bool(allowed), int(count)
