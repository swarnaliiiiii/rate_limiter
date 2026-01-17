from fastapi import APIRouter, Depends
from app.core.metrics import get_dashboard_metrics
from app.storage import redis_client as get_redis

router = APIRouter(prefix="/v1/monitoring")

@router.get("/summary")
async def read_summary(redis_client=Depends(get_redis)):
    """
    Returns the aggregate data for the Decision Overview dashboard cards.
    """
    stats = await get_dashboard_metrics(redis_client)
    return stats