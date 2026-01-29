from fastapi import FastAPI
from app.api.decision import router as decision_router
from app.logging.db import init_db
from app.core.engine import DecisionEngine
from app.api.monitoring import router as monitoring_router
from app.storage.redis_client import _client

app = FastAPI(title="Decision Control Engine")

engine: DecisionEngine | None = None

@app.on_event("startup")
async def startup():
    global engine
    init_db()
    engine = DecisionEngine(_client)

app.include_router(decision_router)
app.include_router(monitoring_router)
