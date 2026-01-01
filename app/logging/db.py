from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.logging.models import Base

DATABASE_URL = "postgresql://rate_limiter:0325@postgres:5432/rate_limiter"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Initialize the database and create tables."""
    Base.metadata.create_all(bind=engine)