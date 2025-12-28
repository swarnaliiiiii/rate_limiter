from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Decision:
    action: str
    reason: str
    triggered_by: str
    retry_after: Optional[int] = None