from app.penalties.states import PenaltyState
from app.core.decision import Decision
from app.core.dag.node import DecisionNode
from app.core.dag.result import NodeResult

class HardBlockNode(DecisionNode):
    def __init__(self, penalty_fsm):
        self.penalty_fsm = penalty_fsm

    async def execute(self, ctx):
        rate_key = f"{ctx.tenant_id}:{ctx.route}:{ctx.user_id}"
        state = await self.penalty_fsm.get_state(rate_key)

        if state in {PenaltyState.TEMP_BLOCK, PenaltyState.BLOCK}:
            ctx.trace.add(
                node="HardBlockNode",
                outcome="BLOCK",
                state=state.name
            )
            return NodeResult(
                Decision(
                    action="BLOCK",
                    reason=f"PENALTY_{state.name}",
                    triggered_by="PenaltyFSM",
                    retry_after=60,
                    trace = ctx.trace
                )
            )

        ctx.trace.add(
            node="HardBlockNode",
            outcome="PASS",
            state=state.name
        )
        return NodeResult()
