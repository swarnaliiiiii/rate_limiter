from app.core.dag.node import DecisionNode
from app.core.dag.result import NodeResult
from app.core.decision import Decision

class RateLimitNode(DecisionNode):
    def __init__(self, engine):
        self.engine = engine

    async def execute(self, ctx):
        rate_key = f"{ctx.tenant_id}:{ctx.route}:{ctx.user_id}"
        limiter = self.engine._get_limiter(ctx)

        if not limiter:
            ctx.trace.add(
                node="RateLimitNode",
                outcome="NO_CONFIG"
            )
            return NodeResult(
                Decision(
                    action="BLOCK",
                    reason="NO_RATE_LIMIT_CONFIG",
                    triggered_by="ConfigResolver",
                    trace= ctx.trace
                )
            )

        allowed, count = await limiter.allow(rate_key, ctx.timestamp)

        if not allowed:
            new_state = await self.engine.penalty_fsm.escalate(rate_key)
            ctx.trace.add(
                node="RateLimitNode",
                outcome="LIMIT_EXCEEDED",
                count=count,
                escalated_to=new_state.name
            )
            return NodeResult(
                Decision(
                    action="BLOCK",
                    reason=f"PENALTY_{new_state.name}",
                    triggered_by="RateLimiter",
                    retry_after=60,
                    trace = ctx.trace
                )
            )

        ctx.trace.add(
            node="RateLimitNode",
            outcome="ALLOW",
            count=count
        )
        return NodeResult()
