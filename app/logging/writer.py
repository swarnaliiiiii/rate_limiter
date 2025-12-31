from app.logging.db import SessionLocal
from app.logging.models import DecisionLog


def log_decision_async(payload: dict):
    """
    Fire-and-forget decision logger.
    Runs outside the request path.
    """
    try:
        db = SessionLocal()
        log = DecisionLog(**payload)
        db.add(log)
        db.commit()
    except Exception as e:
        # Never crash the system due to logging
        print("Decision logging failed:", e)
    finally:
        db.close()
