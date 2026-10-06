from fastapi import APIRouter
from backend.schemas import ConfigResponse, ConfigUpdateRequest
from backend.services.config_service import get_current_config, update_config

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("", response_model=ConfigResponse)
def get_config() -> ConfigResponse:
    return get_current_config()


@router.put("", response_model=ConfigResponse)
def put_config(update_req: ConfigUpdateRequest) -> ConfigResponse:
    return update_config(update_req=update_req)
