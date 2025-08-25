from src.core.services.http_service import HttpService
from src.modules.documents.s3_service import S3Service
from uuid import UUID
from fastapi import Request, File, UploadFile
from src.modules.users.users_models import User
class DocumentsController:
    def __init__(self, http_service: HttpService, s3_service: S3Service):
        self.__http_service = http_service
        self.__s3_service = s3_service

    def handle_knowledge_base_upload(
        agent_id: UUID,
        req: Request,
        file: UploadFile
    ):
        user: User = req.state.user