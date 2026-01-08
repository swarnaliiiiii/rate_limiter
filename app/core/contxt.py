from dataclasses import dataclass, field
from typing import Optional
import time
from app.core.traces import DecisionTrace

@dataclass(frozen=False)
class RequestContext:
    tenant_id: str
    route: str
    method: str
    timestamp: int
    user_id: Optional[str] = None
    trace: DecisionTrace = field(default_factory=DecisionTrace)

    
    @staticmethod
    def from_payload(payload) -> "RequestContext":
        return RequestContext(
            tenant_id=payload.tenant_id,
            user_id=payload.user_id,
            route=payload.route,
            method=payload.method,
            timestamp=int(time.time())
        )