from uuid import UUID
from typing import List, Dict, Any
import asyncio
from fastapi import Request, UploadFile, HTTPException, BackgroundTasks


from sqlalchemy.orm import Session

from src.modules.documents.documents_models import Document, DocumentPublic
from src.modules.users.domain.entities import User

from src.modules.companies.domain.enitities import Company

from src.modules.documents.document_manager import DocumentManager

from src.core.services.encryption_service import EncryptionService
from src.core.services.request_validation_service import RequestValidationService
from src.core.domain.models.http_responses import CommonHttpResponse



class DocumentsController:
    def __init__(
        self, 
        encryption_service: EncryptionService,
        document_manager: DocumentManager
    ):
        self.__encryption_service = encryption_service
        self.__document_manager = document_manager
       

    async def upload_request(
        self,
        req: Request,
        db: Session,
        file: UploadFile
    ):
        user: User = req.state.user
        company: Company = req.state.company

        RequestValidationService.verifiy_ownership(user.user_id, company.user_id)

        allowed_mime_types = [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
            "application/vnd.ms-excel",  # .xls
            "application/vnd.ms-excel.sheet.macroEnabled.12",  # .xlsm
            "application/vnd.ms-excel.sheet.binary.macroEnabled.12",  # .xlsb
            "text/csv",  # .csv
            "application/pdf",  # .pdf
            "text/plain",  # .txt
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
            "application/msword" 
        ]
        
        if file.content_type not in allowed_mime_types:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        asyncio.create_task(
            self.__document_manager.handle_upload(
                file=file,
                company_id=company.company_id,
                user_id=user.user_id,
                db=db
            )
        )
        
        return CommonHttpResponse(
            detail="file uploaded"
        )        
    

    def collection_request(
        self, 
        req: Request,
        db: Session
    ):
        user: User = req.state.user
        company: Company = req.state.company


        RequestValidationService.verifiy_ownership(user.user_id, company.user_id)

        data = self.__document_manager.documents_service.collection(db=db, company_id=company.company_id)

        return [
            self.__to_public(doc) for doc in data
        ]
    
    def delete_request(
        self,
        document_id: UUID,
        req: Request,
        db: Session
    ) ->  CommonHttpResponse:
        user: User = req.state.user
        company: Company = req.state.company

        document_resource: Document = self.__document_manager.documents_service.resource(
            key="document_id",
            value=document_id
        )

        RequestValidationService.verify_resource(
            result=document_resource,
            not_found_message="Document not found"
        )
        

        RequestValidationService.verifiy_ownership(user.user_id, document_resource.company.user_id)

        self.__document_manager.document_level_deletion(
            document_id=document_resource.document_id,
            company_id=document_resource.company.company_id,
            user_id=document_resource.company.user_id,
            filename=document_resource.filename,
            db=db
        )

        return CommonHttpResponse(
            detail="Document deleted"
        )

    def __to_public(self, data: Document) -> DocumentPublic:
        document = DocumentPublic(
            document_id=str(data.document_id),
            company_id=str(data.company_id),
            filename=data.filename,
            file_type=data.file_type,
            url=self.__encryption_service.decrypt(data.url),
            uploaded_at=data.uploaded_at
        )

        return document

