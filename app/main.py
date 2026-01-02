from fastapi import FastAPI
from app.api.decision import router as decision_router
from app.logging.db import init_db
from app.core.engine import DecisionEngine

app = FastAPI(title="Decision Control Engine")

engine: DecisionEngine | None = None

@app.on_event("startup")
def startup():
    global engine
    init_db()
    engine = DecisionEngine()

app.include_router(decision_router)
