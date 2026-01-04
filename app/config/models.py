from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.logging.db import Base

class RateLimitConfig(Base):
    __tablename__ = "rate_limit_configs"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, nullable=False)
    route = Column(String, nullable=True, index=True)
    requests = Column(Integer, nullable=False)
    window_seconds = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
