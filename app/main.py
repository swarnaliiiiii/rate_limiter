from fastapi import FastAPI
from app.api.decision import router as decision_router

app = FastAPI(title="Decision Control Engine")

app.include_router(decision_router)
