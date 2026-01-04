from app.logging.db import SessionLocal
from app.config.models import RateLimitConfig

def get_rate_limit_for_tenant(tenant_id: str, route: str | None):
    db = SessionLocal()
    try:
        # 1. Route-specific override
        rule = (
            db.query(RateLimitConfig)
            .filter(
                RateLimitConfig.tenant_id == tenant_id,
                RateLimitConfig.route == route
            )
            .order_by(RateLimitConfig.created_at.desc())
            .first()
        )

        if rule:
            return rule

        # 2. Tenant default (route IS NULL)
        return (
            db.query(RateLimitConfig)
            .filter(
                RateLimitConfig.tenant_id == tenant_id,
                RateLimitConfig.route.is_(None)
            )
            .order_by(RateLimitConfig.created_at.desc())
            .first()
        )
    finally:
        db.close()
