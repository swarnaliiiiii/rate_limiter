from typing import Optional
from app.core.decision import Decision

class NodeResult:
    def __init__(self, decision: Optional[Decision] = None):
        self.decision = decision

    @property
    def is_terminal(self) -> bool:
        return self.decision is not None
