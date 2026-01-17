from datetime import datetime
from sqlalchemy import func
from app.logging.db import SessionLocal
from app.logging.models import DecisionLog
import redis.asyncio as redis
from app.config.repo import RateLimitConfig # Adjust import as needed

async def get_dashboard_metrics(redis_client: redis.Redis):
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Fetch Real-time 'Today' counts from Redis (Fast Path)
    # We use these for the "vs yesterday" logic later
    allow_today = await redis_client.get(f"stats:{today_str}:allow") or 0
    block_today = await redis_client.get(f"stats:{today_str}:block") or 0
    throttle_today = await redis_client.get(f"stats:{today_str}:throttle") or 0
    
    # 2. Count Active Penalties in Redis
    # Scans for keys your PenaltyFSM has marked (e.g., penalty:info:client_1)
    _, penalty_keys = await redis_client.scan(match="penalty:info:*")
    
    # 3. Fetch Total Counts from Postgres (Historical Path)
    db = SessionLocal()
    try:
        # Grouping by action to get totals for the 'Decision Overview' cards
        totals = db.query(DecisionLog.action, func.count(DecisionLog.id)).group_by(DecisionLog.action).all()
        totals_map = {action: count for action, count in totals}
        
        # Count total unique rules from your rate_limit_configs table
        total_rules = db.query(RateLimitConfig).count()
    finally:
        db.close()

    return {
        "allow": totals_map.get("ALLOW", 0),
        "blocked": totals_map.get("BLOCK", 0),
        "throttled": totals_map.get("THROTTLE", 0),
        "penalized_keys": len(penalty_keys),
        "active_rules": total_rules,
        "today": {
            "allow": int(allow_today),
            "block": int(block_today),
            "throttle": int(throttle_today)
        }
    }