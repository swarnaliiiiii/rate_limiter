from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.core.contxt import RequestContext
from app.core.engine import DecisionEngine

router = APIRouter()
engine = DecisionEngine()


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
def check_decision(payload: DecisionRequest):
    ctx = RequestContext.from_payload(payload)
    decision = engine.evaluate(ctx)

    return DecisionResponse(
        action=decision.action,
        reason=decision.reason,
        triggered_by=decision.triggered_by,
        retry_after=decision.retry_after
    )
