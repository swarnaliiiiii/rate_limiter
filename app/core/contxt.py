from dataclasses import dataclass
from typing import Optional
import time

@dataclass(frozen=True)
class RequestContext:
    tenant_id: str
    route: str
    method: str
    timestamp: int
    user_id: Optional[str] = None
    
    @staticmethod
    def from_payload(payload) -> "RequestContext":
        return RequestContext(
            tenant_id=payload.tenant_id,
            user_id=payload.user_id,
            route=payload.route,
            method=payload.method,
            timestamp=int(time.time())
        )