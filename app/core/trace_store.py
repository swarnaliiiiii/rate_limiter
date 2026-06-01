import json
from dataclasses import asdict
from app.storage.redis_client import get_redis
from app.core.traces import DecisionTrace, TraceStep

# Traces are short-lived debugging artifacts, not permanent records.
TRACE_TTL = 3600  # 1 hour


def _key(decision_id: str) -> str:
    return f"trace:{decision_id}"


async def save_trace(decision_id: str, trace: DecisionTrace) -> None:
    payload = {
        "decision_id": decision_id,
        "steps": [asdict(step) for step in trace.steps],
    }
    await get_redis().setex(_key(decision_id), TRACE_TTL, json.dumps(payload))


async def load_trace(decision_id: str) -> dict | None:
    raw = await get_redis().get(_key(decision_id))
    if raw is None:
        return None
    return json.loads(raw)
