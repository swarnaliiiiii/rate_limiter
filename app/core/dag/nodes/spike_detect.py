from app.core.dag.node import DecisionNode
from app.core.dag.result import NodeResult
from app.abuse.redis_stats import get_count

BASELINE_WINDOW = 300
CURRENT_WINDOW = 60
SPIKE_MULTIPLIER = 3
MIN_REQUESTS = 10

class SpikeDetectionNode(DecisionNode):
    def __init__(self, penalty_fsm):
        self.penalty_fsm = penalty_fsm

    def execute(self, ctx):
        key = f"{ctx.tenant_id}:{ctx.route}:{ctx.user_id}"

        baseline = get_count(key, BASELINE_WINDOW)
        current = get_count(key, CURRENT_WINDOW)

        if baseline < MIN_REQUESTS:
            ctx.trace.add(
                node="SpikeDetectionNode",
                outcome="SKIPPED_LOW_BASELINE",
                baseline=baseline,
                current=current
            )
            return NodeResult()

        avg_per_min = baseline / (BASELINE_WINDOW / 60)

        if current > avg_per_min * SPIKE_MULTIPLIER:
            new_state = self.penalty_fsm.escalate(key)

            ctx.trace.add(
                node="SpikeDetectionNode",
                outcome="SPIKE_DETECTED",
                baseline_avg=avg_per_min,
                current=current,
                escalated_to=new_state.name
            )
            return NodeResult()  # Do NOT block

        ctx.trace.add(
            node="SpikeDetectionNode",
            outcome="PASS",
            baseline_avg=avg_per_min,
            current=current
        )
        return NodeResult()
