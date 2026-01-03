from app.logging.db import SessionLocal
from app.config.models import RateLimitConfig

def get_rate_limit_for_tenant(tenant_id: str, route: str | None):
    db = SessionLocal()
    try:
        return (
            db.query(RateLimitConfig)
            .filter(RateLimitConfig.tenant_id == tenant_id, RateLimitConfig.route == route)
            .order_by(RateLimitConfig.created_at.desc())
            .first()
        )
    finally:
        db.close()
        
def get_tenant_config_rule(tenant_id: str):
    db = SessionLocal()
    try:
        return (
            db.query(RateLimitConfig)
            .filter(RateLimitConfig.tenant_id == tenant_id, RateLimitConfig.route.is_(None))
            .order_by(RateLimitConfig.created_at.desc())
            .first()
        )
    finally:
        db.close()
