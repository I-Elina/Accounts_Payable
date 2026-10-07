from fastapi import APIRouter, Query
from backend.schemas import StatsResponse
from backend.services.stats_service import get_stats

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=StatsResponse)
def get_dashboard_stats(upload_id: int | None = Query(None)) -> StatsResponse:
    return get_stats(upload_id=upload_id)
