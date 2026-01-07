from app.core.dag.node import DecisionNode
from app.core.dag.result import NodeResult
from app.core.decision import Decision

class AllowNode(DecisionNode):
    def execute(self, ctx):
        return NodeResult(
            Decision(
                action="ALLOW",
                reason="WITHIN_RATE_LIMIT",
                triggered_by="SlidingWindowLimiter"
            )
        )
