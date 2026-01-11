from app.core.contxt import RequestContext
from app.core.decision import Decision
from app.limiter.redis_sw import RedisSlidingWindowLimiter
from app.penalties.fsm import PenaltyFSM
from app.config.repo import get_rate_limit_rule

from app.core.dag.nodes.hard_block import HardBlockNode
from app.core.dag.nodes.rate_limit import RateLimitNode
from app.core.dag.nodes.allow import AllowNode
from app.core.dag.nodes.spike_detect import SpikeDetectionNode




class DecisionEngine:
    def __init__(self):
        self.limiters = {}         
        self.penalty_fsm = PenaltyFSM()

        self.pipeline = [
            HardBlockNode(self.penalty_fsm),
            SpikeDetectionNode(self.penalty_fsm),
            RateLimitNode(self),
            AllowNode()
        ]

    def _get_limiter(self, ctx: RequestContext):
        rule = get_rate_limit_rule(
            tenant_id=ctx.tenant_id,
            route=ctx.route,
            user_id=ctx.user_id
        )

        if not rule:
            return None

        limiter_key = f"{rule.tenant_id}:{rule.route}:{rule.user_id}"

        if limiter_key in self.limiters:
            return self.limiters[limiter_key]

        limiter = RedisSlidingWindowLimiter(
            window_size=rule.window_seconds,
            limit=rule.requests
        )

        self.limiters[limiter_key] = limiter
        return limiter

    def evaluate(self, ctx: RequestContext) -> Decision:
        for node in self.pipeline:
            result = node.execute(ctx)
            if result.is_terminal:
                result.decision.trace = ctx.trace
                return result.decision
