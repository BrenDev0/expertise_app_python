from  fastapi import APIRouter, UploadFile, Request, File
from src.modules.documents.s3_service import S3Service
from src.core.models.http_responses import CommonHttpResponse
from uuid import UUID


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

@router.post("/secure/knowlege-base", status_code=201, response_model=CommonHttpResponse)
def secure_upload(
    agent_id: UUID,
    req: Request,
    file: UploadFile = File(...)
):
    pass