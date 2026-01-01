from fastapi import FastAPI
from app.api.decision import router as decision_router
from app.logging.db import init_db

app = FastAPI(title="Decision Control Engine")

@app.on_event("startup")
def startup():
    init_db()

app.include_router(decision_router)
