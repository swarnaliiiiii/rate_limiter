from dataclasses import dataclass
from typing import Optional
from app.core.traces import DecisionTrace

@dataclass(frozen=True)
class Decision:
    action: str
    reason: str
    triggered_by: str
    retry_after: Optional[int] = None
    trace: Optional[DecisionTrace] = None