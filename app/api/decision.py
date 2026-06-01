from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.core.contxt import RequestContext
from app.core.engine import DecisionEngine
from app.core.trace_store import load_trace
from app.logging.writer import log_decision_async
from app.storage.redis_client import get_redis
# from app.main import engine


router = APIRouter()
engine = DecisionEngine(get_redis())


class DecisionRequest(BaseModel):
    tenant_id: str
    user_id: Optional[str] = None
    route: str
    method: str


class DecisionResponse(BaseModel):
    decision_id: str
    action: str
    reason: str
    triggered_by: str
    retry_after: Optional[int] = None


@router.post("/v1/decision/check", response_model=DecisionResponse)
async def check_decision(payload: DecisionRequest, background_tasks: BackgroundTasks):
    ctx = RequestContext.from_payload(payload)
    decision = await engine.evaluate(ctx)

    background_tasks.add_task(
        log_decision_async,
        {
            "tenant_id": ctx.tenant_id,
            "route": ctx.route,
            "action": decision.action,
            "reason": decision.reason,
            "triggered_by": decision.triggered_by,
        }
    )

    return DecisionResponse(
        decision_id=decision.decision_id,
        action=decision.action,
        reason=decision.reason,
        triggered_by=decision.triggered_by,
        retry_after=decision.retry_after
    )


@router.get("/v1/decision/trace/{decision_id}")
async def get_decision_trace(decision_id: str):
    trace = await load_trace(decision_id)
    if trace is None:
        raise HTTPException(
            status_code=404,
            detail=f"No trace found for decision_id={decision_id} (it may have expired)",
        )
    return trace
