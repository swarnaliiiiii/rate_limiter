from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from app.core.contxt import RequestContext
from app.core.engine import DecisionEngine
from app.logging.writer import log_decision_async
from app.storage.redis_client import redis_client
# from app.main import engine


router = APIRouter()
engine = DecisionEngine(redis_client)


class DecisionRequest(BaseModel):
    tenant_id: str
    user_id: Optional[str] = None
    route: str
    method: str


class DecisionResponse(BaseModel):
    action: str
    reason: str
    triggered_by: str
    retry_after: Optional[int] = None


@router.post("/v1/decision/check", response_model=DecisionResponse)
def check_decision(payload: DecisionRequest, background_tasks: BackgroundTasks):
    ctx = RequestContext.from_payload(payload)
    decision = engine.evaluate(ctx)

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
        action=decision.action,
        reason=decision.reason,
        triggered_by=decision.triggered_by,
        retry_after=decision.retry_after
    )
