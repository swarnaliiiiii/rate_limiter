import time
from app.penalties.states import PenaltyState
from app.storage.redis_client import get_redis


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

    async def get_state(self, scope: str) -> PenaltyState:
        val = await get_redis().get(self._key(scope))
        return PenaltyState(val) if val else PenaltyState.NORMAL

    async def escalate(self, scope: str) -> PenaltyState:
        current = await self.get_state(scope)
        next_state = self.TRANSITIONS[current]

        ttl = self.STATE_TTL.get(next_state)
        if ttl:
            await get_redis().setex(self._key(scope), ttl, next_state.value)
        else:
            await get_redis().set(self._key(scope), next_state.value)

        return next_state
