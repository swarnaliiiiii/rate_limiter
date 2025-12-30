from app.core.contxt import RequestContext
from app.core.decision import Decision
from app.limiter.redis_sw import RedisSlidingWindowLimiter
from app.penalties.fsm import PenaltyFSM
from app.penalties.states import PenaltyState




class DecisionEngine:
    def __init__(self):
        # v1 configuration (hardcoded for now)
        self.rate_limiter = RedisSlidingWindowLimiter(
            window_size=60,   # 60 seconds
            limit=5           # 5 requests per window
        )
        
        self.penalty_fsm = PenaltyFSM()

    def evaluate(self, ctx: RequestContext) -> Decision:
        # Key defines rate limiting scope
        key = f"{ctx.tenant_id}:{ctx.route}"

        state = self.penalty_fsm.get_state(key)

        # Hard block states
        if state in {PenaltyState.TEMP_BLOCK, PenaltyState.BLOCK}:
            return Decision(
                action="BLOCK",
                reason=f"PENALTY_{state}",
                triggered_by="PenaltyFSM",
                retry_after=60
            )

        allowed, count = self.rate_limiter.allow(key, ctx.timestamp)

        if not allowed:
            new_state = self.penalty_fsm.escalate(key)

            action = "THROTTLE" if new_state == PenaltyState.THROTTLE else "BLOCK"

            return Decision(
                action=action,
                reason=f"PENALTY_{new_state}",
                triggered_by="PenaltyFSM",
                retry_after=60
            )

        return Decision(
            action="ALLOW",
            reason="WITHIN_RATE_LIMIT",
            triggered_by="SlidingWindowLimiter"
        )

