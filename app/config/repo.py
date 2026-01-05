from sqlalchemy import or_, and_
from app.logging.db import SessionLocal
from app.config.models import RateLimitConfig

def get_rate_limit_rule(tenant_id: str, route: str, user_id: str | None):
    db = SessionLocal()
    try:
        # 1. tenant + route + user
        rule = db.query(RateLimitConfig).filter(
            RateLimitConfig.tenant_id == tenant_id,
            RateLimitConfig.route == route,
            RateLimitConfig.user_id == user_id
        ).first()
        if rule:
            return rule

        # 2. tenant + route
        rule = db.query(RateLimitConfig).filter(
            RateLimitConfig.tenant_id == tenant_id,
            RateLimitConfig.route == route,
            RateLimitConfig.user_id.is_(None)
        ).first()
        if rule:
            return rule

        # 3. tenant default
        rule = db.query(RateLimitConfig).filter(
            RateLimitConfig.tenant_id == tenant_id,
            RateLimitConfig.route.is_(None),
            RateLimitConfig.user_id.is_(None)
        ).first()
        if rule:
            return rule

        # 4. global default
        rule = db.query(RateLimitConfig).filter(
            RateLimitConfig.tenant_id == "__global__"
        ).first()
        return rule

    finally:
        db.close()
