from app.core.dag.node import DecisionNode
from app.core.dag.result import NodeResult
from app.core.decision import Decision
from app.core.contxt import RequestContext

# Tunables
SHORT_WINDOW = 10        
LONG_WINDOW = 120        
BURST_MULTIPLIER = 5
MIN_RPS = 10             

class BurstDetectionNode(DecisionNode):
    name = "burst_detection"

    def __init__(self, redis_client):
        self.redis = redis_client # Use the injected client

    async def execute(self, ctx: RequestContext) -> NodeResult:
        key = f"{ctx.tenant_id}:{ctx.route}"
        short_key = f"burst:short:{key}"
        long_key = f"burst:long:{key}"

        # Use self.redis and await the async calls
        short_count = await self.redis.incr(short_key)
        await self.redis.expire(short_key, SHORT_WINDOW)

        long_count = await self.redis.incr(long_key)
        await self.redis.expire(long_key, LONG_WINDOW)

        # Calculate rates
        burst_rps = short_count / SHORT_WINDOW
        baseline_rps = long_count / LONG_WINDOW

        anomaly = (
            burst_rps > baseline_rps * BURST_MULTIPLIER
            and burst_rps >= MIN_RPS
        )

        ctx.trace.add(
            node=self.name,
            data={
                "short_rps": round(burst_rps, 2),
                "baseline_rps": round(baseline_rps, 2),
                "multiplier": BURST_MULTIPLIER,
                "anomaly": anomaly,
            },
        )

        if anomaly:
            return NodeResult(
                continue_pipeline=False,
                decision=Decision(
                    action="THROTTLE",
                    reason="SUDDEN_BURST_DETECTED",
                    triggered_by="BurstDetector",
                ),
            )

        return NodeResult(continue_pipeline=True)