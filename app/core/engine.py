from app.core.contxt import RequestContext
from app.core.decision import Decision
from app.limiter.redis_sw import RedisSlidingWindowLimiter
from app.penalties.fsm import PenaltyFSM
from app.penalties.states import PenaltyState
from app.config.repo import get_rate_limit_for_tenant

class DecisionEngine:
    def __init__(self):
        self.limiters = {}
        self.penalty_fsm = PenaltyFSM()

    def _get_limiter(self, tenant_id: str, route: str):
        key = f"{tenant_id}:{route}"

        if key in self.limiters:
            return self.limiters[key]

        config = get_rate_limit_for_tenant(tenant_id, route)

        if config:
            limiter = RedisSlidingWindowLimiter(
                window_size=config.window_seconds,
                limit=config.requests
            )
        else:
            limiter = RedisSlidingWindowLimiter(
                window_size=60,
                limit=5
            )

        self.limiters[key] = limiter
        return limiter

    def evaluate(self, ctx: RequestContext) -> Decision:
        key = f"{ctx.tenant_id}:{ctx.route}"

        state = self.penalty_fsm.get_state(key)
        if state in {PenaltyState.TEMP_BLOCK, PenaltyState.BLOCK}:
            return Decision(
                action="BLOCK",
                reason=f"PENALTY_{state}",
                triggered_by="PenaltyFSM",
                retry_after=60
            )

        limiter = self._get_limiter(ctx.tenant_id, ctx.route)
        allowed, _ = limiter.allow(key, ctx.timestamp)

        if not allowed:
            new_state = self.penalty_fsm.escalate(key)
            return Decision(
                action="BLOCK",
                reason=f"PENALTY_{new_state}",
                triggered_by="PenaltyFSM",
                retry_after=60
            )

        return Decision(
            action="ALLOW",
            reason="WITHIN_RATE_LIMIT",
            triggered_by="SlidingWindowLimiter"
        )
