import os
import redis.asyncio as redis # Use asyncio version for your async engine

# Create the client instance once
_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "decision-redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

# The callable function FastAPI needs
async def get_redis():
    return _client