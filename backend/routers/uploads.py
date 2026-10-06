from fastapi import APIRouter, File, Form, UploadFile
from backend.schemas import UploadListResponse, UploadResponse
from backend.services.upload_service import list_uploads, process_upload

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


@router.post("", response_model=UploadResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    uploaded_by: str | None = Form(None),
    use_history: bool = Form(False),
) -> UploadResponse:
    return await process_upload(file=file, uploaded_by=uploaded_by, use_history=use_history)


@router.get("", response_model=UploadListResponse)
def get_uploads() -> UploadListResponse:
    return list_uploads()
