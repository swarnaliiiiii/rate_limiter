from app.logging.db import SessionLocal
from app.config.models import RateLimitConfig

def get_rate_limit_for_tenant(tenant_id: str):
    db = SessionLocal()
    try:
        return (
            db.query(RateLimitConfig)
            .filter(RateLimitConfig.tenant_id == tenant_id)
            .first()
        )
    finally:
        db.close()
