from app.core.contxt import RequestContext
from app.core.decision import Decision
from app.limiter.redis_sw import RedisSlidingWindowLimiter
from app.penalties.fsm import PenaltyFSM
from app.penalties.states import PenaltyState
from app.config.repo import get_rate_limit_rule


class DecisionEngine:
    def __init__(self):
        # Cache limiter per resolved config rule
        self.limiters = {}
        self.penalty_fsm = PenaltyFSM()

    def _get_limiter(self, ctx: RequestContext):
        """
        Resolve rate limit config in this order:
        1. tenant + route + user
        2. tenant + route
        3. tenant only
        4. global default
        """

        rule = get_rate_limit_rule(
            tenant_id=ctx.tenant_id,
            route=ctx.route,
            user_id=ctx.user_id
        )

        if not rule:
            return Decision(
                action="BLOCK",
                reason="NO_RATE_LIMIT_CONFIG",
                triggered_by="ConfigResolver"
            )

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
        """
        Main decision pipeline
        """

        rate_key = f"{ctx.tenant_id}:{ctx.route}:{ctx.user_id}"

        # --- Penalty check ---
        state = self.penalty_fsm.get_state(rate_key)
        if state in {PenaltyState.TEMP_BLOCK, PenaltyState.BLOCK}:
            return Decision(
                action="BLOCK",
                reason=f"PENALTY_{state.name}",
                triggered_by="PenaltyFSM",
                retry_after=60
            )

        # --- Rate limit check ---
        limiter = self._get_limiter(ctx)

        if not limiter:
            return Decision(
                action="BLOCK",
                reason="NO_RATE_LIMIT_CONFIG",
                triggered_by="ConfigResolver"
            )

        allowed, _ = limiter.allow(rate_key, ctx.timestamp)

        if not allowed:
            new_state = self.penalty_fsm.escalate(rate_key)

            return Decision(
                action="BLOCK",
                reason=f"PENALTY_{new_state.name}",
                triggered_by="RateLimiter",
                retry_after=60
            )

        # --- Allowed ---
        return Decision(
            action="ALLOW",
            reason="WITHIN_RATE_LIMIT",
            triggered_by="SlidingWindowLimiter"
        )
