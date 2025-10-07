from uuid import UUID
from typing import List, Dict, Any
import asyncio
from fastapi import Request, UploadFile, HTTPException, BackgroundTasks


from sqlalchemy.orm import Session

from src.modules.documents.documents_models import Document, DocumentPublic
from src.modules.users.domain.entities import User
from src.modules.companies.companies_models import Company

from src.modules.documents.document_manager import DocumentManager

from src.core.services.http_service import HttpService
from src.core.domain.models.http_responses import CommonHttpResponse



class DocumentsController:
    def __init__(
        self, 
        http_service: HttpService, 
        document_manager: DocumentManager
    ):
        self.__http_service = http_service
        self.__document_manager = document_manager
       

    async def upload_request(
        self,
        req: Request,
        db: Session,
        file: UploadFile
    ):
        user: User = req.state.user
        company: Company = self.__http_service.request_validation_service.verify_company_in_request_state(req=req, db=db)

        company_resource: Company = self.__http_service.request_validation_service.verify_resource(
            service_key="companies_service",
            params={
                "db": db,
                "company_id": company.company_id
            },
            not_found_message="Company not found"
        )

        self.__http_service.request_validation_service.validate_action_authorization(user.user_id, company_resource.user_id)

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
        company: Company = self.__http_service.request_validation_service.verify_company_in_request_state(req=req, db=db)

        company_resource: Company = self.__http_service.request_validation_service.verify_resource(
            service_key="companies_service",
            params={
                "db": db,
                "company_id": company.company_id
            },
            not_found_message="Company not found"
        )

        self.__http_service.request_validation_service.validate_action_authorization(user.user_id, company_resource.user_id)

        data = self.__document_manager.documents_service.collection(db=db, company_id=company_resource.company_id)

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
        company: Company = self.__http_service.request_validation_service.verify_company_in_request_state(req=req, db=db)

        document_resource: Document = self.__http_service.request_validation_service.verify_resource(
            service_key="documents_service",
            params={
                "db": db,
                "document_id": document_id
            },
            not_found_message="Document Not found"
        )

        self.__http_service.request_validation_service.validate_action_authorization(user.user_id, document_resource.company.user_id)

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
            url=self.__http_service.encryption_service.decrypt(data.url),
            uploaded_at=data.uploaded_at
        )

        return document

