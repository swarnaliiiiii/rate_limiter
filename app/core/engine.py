from app.core.contxt import RequestContext
from app.core.decision import Decision
from app.limiter.sliding_window import SlidingWindowLimiter


class DecisionEngine:
    def __init__(self):
        # v1 configuration (hardcoded for now)
        self.rate_limiter = SlidingWindowLimiter(
            window_size=60,   # 60 seconds
            limit=5           # 5 requests per window
        )

    def evaluate(self, ctx: RequestContext) -> Decision:
        # Key defines rate limiting scope
        key = f"{ctx.tenant_id}:{ctx.route}"

        allowed, count = self.rate_limiter.allow(key, ctx.timestamp)

        if not allowed:
            return Decision(
                action="BLOCK",
                reason="RATE_LIMIT_EXCEEDED",
                triggered_by="SlidingWindowLimiter",
                retry_after=60
            )

        return Decision(
            action="ALLOW",
            reason="WITHIN_RATE_LIMIT",
            triggered_by="SlidingWindowLimiter"
        )
