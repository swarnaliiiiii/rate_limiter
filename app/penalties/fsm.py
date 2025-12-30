import time
from app.penalties.states import PenaltyState
from app.storage.redis_client import redis_client


class PenaltyFSM:
    """
    Tracks abuse escalation per key using Redis.
    """

    STATE_TTL = {
        PenaltyState.WARN: 60,
        PenaltyState.THROTTLE: 120,
        PenaltyState.TEMP_BLOCK: 300,
        PenaltyState.BLOCK: 900,
    }

    TRANSITIONS = {
        PenaltyState.NORMAL: PenaltyState.WARN,
        PenaltyState.WARN: PenaltyState.THROTTLE,
        PenaltyState.THROTTLE: PenaltyState.TEMP_BLOCK,
        PenaltyState.TEMP_BLOCK: PenaltyState.BLOCK,
        PenaltyState.BLOCK: PenaltyState.BLOCK,
    }

    def _key(self, scope: str) -> str:
        return f"penalty:{scope}"

    def get_state(self, scope: str) -> PenaltyState:
        val = redis_client.get(self._key(scope))
        return PenaltyState(val) if val else PenaltyState.NORMAL

    def escalate(self, scope: str) -> PenaltyState:
        current = self.get_state(scope)
        next_state = self.TRANSITIONS[current]

        ttl = self.STATE_TTL.get(next_state)
        if ttl:
            redis_client.setex(self._key(scope), ttl, next_state.value)
        else:
            redis_client.set(self._key(scope), next_state.value)

        return next_state
