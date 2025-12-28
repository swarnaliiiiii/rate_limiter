from app.core.decision import Decision
from app.core.contxt import RequestContext

class DecisionEngine:

    def evaluate(self, context: RequestContext) -> Decision:
        return Decision(
            action="allow",
            reason="default allow",
            triggered_by="engine",
            retry_after=None
        )