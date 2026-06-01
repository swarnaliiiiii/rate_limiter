from fastapi import FastAPI
from app.api.decision import router as decision_router
from app.logging.db import init_db
from app.api.monitoring import router as monitoring_router

app = FastAPI(title="Decision Control Engine")


@app.on_event("startup")
async def startup():
    # The DecisionEngine is instantiated in app.api.decision; here we only
    # need to ensure the database tables exist.
    init_db()

app.include_router(decision_router)
app.include_router(monitoring_router)
