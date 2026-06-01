from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.decision import router as decision_router
from app.logging.db import init_db
from app.api.monitoring import router as monitoring_router

app = FastAPI(title="Decision Control Engine")

# Allow the static frontend (opened from a file or any local static server)
# to call the API from the browser. Open in dev; tighten allow_origins for prod.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    # The DecisionEngine is instantiated in app.api.decision; here we only
    # need to ensure the database tables exist.
    init_db()

app.include_router(decision_router)
app.include_router(monitoring_router)

# Serve the static frontend at "/". Mounted last so the API routes above
# take precedence; html=True serves index.html for the root path.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
