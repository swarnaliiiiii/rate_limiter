from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class DecisionLog(Base):
    __tablename__ = "decision_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True)
    route = Column(String, index=True)
    action = Column(String)
    reason = Column(String)
    triggered_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
