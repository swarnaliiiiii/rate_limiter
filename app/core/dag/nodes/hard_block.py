from app.penalties.states import PenaltyState
from app.core.decision import Decision
from app.core.dag.node import DecisionNode
from app.core.dag.result import NodeResult

class HardBlockNode(DecisionNode):
    def __init__(self, penalty_fsm):
        self.penalty_fsm = penalty_fsm

    def execute(self, ctx):
        key = f"{ctx.tenant_id}:{ctx.route}:{ctx.user_id}"
        state = self.penalty_fsm.get_state(key)

        if state in {PenaltyState.TEMP_BLOCK, PenaltyState.BLOCK}:
            return NodeResult(
                Decision(
                    action="BLOCK",
                    reason=f"PENALTY_{state}",
                    triggered_by="PenaltyFSM",
                    retry_after=60
                )
            )

        return NodeResult()
