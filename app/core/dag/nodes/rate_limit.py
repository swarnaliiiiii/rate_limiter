from app.core.dag.node import DecisionNode
from app.core.dag.result import NodeResult
from app.core.decision import Decision

class RateLimitNode(DecisionNode):
    def __init__(self, limiter, penalty_fsm):
        self.limiter = limiter
        self.penalty_fsm = penalty_fsm

    def execute(self, ctx):
        key = f"{ctx.tenant_id}:{ctx.route}:{ctx.user_id}"
        allowed, _ = self.limiter.allow(key, ctx.timestamp)

        if not allowed:
            new_state = self.penalty_fsm.escalate(key)
            return NodeResult(
                Decision(
                    action="BLOCK",
                    reason=f"PENALTY_{new_state}",
                    triggered_by="RateLimit",
                    retry_after=60
                )
            )

        return NodeResult()
