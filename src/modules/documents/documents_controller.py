from src.core.services.http_service import HttpService
from src.modules.documents.s3_service import S3Service
from uuid import UUID
from fastapi import Request, UploadFile, HTTPException
from src.modules.documents.documents_models import Document, DocumentPublic
from src.modules.users.users_models import User
from sqlalchemy.orm import Session
from src.modules.companies.companies_models import Company
from src.core.models.http_responses import CommonHttpResponse
from src.modules.documents.document_manager import DocumentManager
import asyncio


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
        company_id = self.__http_service.request_validation_service.verify_company_in_request_state(req=req)

        company_resource: Company = self.__http_service.request_validation_service.verify_resource(
            service_key="companies_service",
            params={
                "db": db,
                "company_id": company_id
            },
            not_found_message="Company not found"
        )

        self.__http_service.request_validation_service.validate_action_authorization(user.user_id, company_resource.user_id)

        asyncio.create_task(
            self.__document_manager.handle_upload(
                file=file,
                company_id=company_resource.company_id,
                user_id=company_resource.user_id,
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
        company_id = self.__http_service.request_validation_service.verify_company_in_request_state(req=req)

        company_resource: Company = self.__http_service.request_validation_service.verify_resource(
            service_key="documents_service",
            params={
                "db": db,
                "company_id": company_id
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
        company_id = self.__http_service.request_validation_service.verify_company_in_request_state(req=req)

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
            url=self.__http_service.encryption_service.decrypt(data.url),
            uploaded_at=data.uploaded_at
        )

        return document

