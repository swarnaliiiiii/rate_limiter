from datetime import datetime
import json
from app.core.contxt import RequestContext
from app.core.decision import Decision
from app.limiter.redis_sw import RedisSlidingWindowLimiter
from app.penalties.fsm import PenaltyFSM
from app.config.repo import get_rate_limit_rule

# Pipeline Nodes
from app.core.dag.nodes.hard_block import HardBlockNode
from app.core.dag.nodes.rate_limit import RateLimitNode
from app.core.dag.nodes.allow import AllowNode
from app.core.dag.nodes.spike_detect import SpikeDetectionNode
from app.core.dag.nodes.burst_detect import BurstDetectionNode

class DecisionEngine:
    def __init__(self, redis_client):
        self.redis = redis_client  # Injected Redis client for metrics
        self.limiters = {}         
        self.penalty_fsm = PenaltyFSM()

        # Decision Pipeline
        self.pipeline = [
            HardBlockNode(self.penalty_fsm),
            RateLimitNode(self),
            SpikeDetectionNode(self.penalty_fsm),
            BurstDetectionNode(),
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

    async def evaluate(self, ctx: RequestContext) -> Decision:
        for node in self.pipeline:
            result = node.execute(ctx)
            
            # result is a NodeResult, result.decision is the actual Decision
            if result.is_terminal:
                decision = result.decision
                
                # Update Real-Time Metrics before returning
                await self._record_metrics(ctx, decision)
                
                return decision

    async def _record_metrics(self, ctx: RequestContext, decision: Decision):
        """
        Internal helper to update Redis counters and publish live updates.
        """
        today_str = datetime.now().strftime("%Y-%m-%d")
        action_key = decision.action.lower() # allow, block, or throttle
        
        # 1. Atomic Increment for Dashboard Cards
        # Format: stats:2026-01-17:allow
        await self.redis.incr(f"stats:{today_str}:{action_key}")
        
        # 2. (Optional) Publish to WebSocket channel for the live logs
        event_payload = {
            "tenant_id": ctx.tenant_id,
            "route": ctx.route,
            "action": decision.action,
            "reason": decision.reason,
            "timestamp": datetime.now().isoformat()
        }
        await self.redis.publish("live_decisions", json.dumps(event_payload))