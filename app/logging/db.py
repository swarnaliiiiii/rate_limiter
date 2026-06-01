import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.logging.models import Base

# Read from the environment (docker-compose injects DATABASE_URL). The
# fallback is for local dev only — don't ship real credentials in code.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://rate_limiter:rate_limiter@localhost:5432/rate_limiter",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# expire_on_commit=False lets returned ORM objects keep their loaded values
# after the session commits/closes, so callers can read attributes off a
# detached instance without triggering a lazy reload.
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def init_db():
    """Initialize the database and create tables."""
    Base.metadata.create_all(bind=engine)