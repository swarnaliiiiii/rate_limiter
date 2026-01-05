from sqlalchemy import or_, and_
from app.logging.db import SessionLocal
from app.config.models import RateLimitConfig

def get_rate_limit_config(tenant_id, route, user_id):
    db = SessionLocal()
    try:
        return (
            db.query(RateLimitConfig)
            .filter(
                RateLimitConfig.tenant_id == tenant_id,
                or_(
                    # Highest priority
                    and_(
                        RateLimitConfig.route == route,
                        RateLimitConfig.user_id == user_id
                    ),
                    # Route-level
                    and_(
                        RateLimitConfig.route == route,
                        RateLimitConfig.user_id.is_(None)
                    ),
                    # Tenant-level
                    and_(
                        RateLimitConfig.route.is_(None),
                        RateLimitConfig.user_id.is_(None)
                    )
                )
            )
            .order_by(
                RateLimitConfig.user_id.desc().nullslast(),
                RateLimitConfig.route.desc().nullslast()
            )
            .first()
        )
    finally:
        db.close()
