from fastapi import APIRouter
from backend.schemas import HealthResponse
from backend.settings import AI_MODE

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", ai_mode=AI_MODE)
