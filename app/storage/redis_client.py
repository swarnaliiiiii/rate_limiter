import os
import redis.asyncio as redis 


_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "decision-redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

async def get_redis():
    return _client