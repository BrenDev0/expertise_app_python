from src.core.services.http_service import HttpService
from src.modules.documents.s3_service import S3Service
from uuid import UUID
from fastapi import Request, UploadFile, HTTPException
from src.modules.documents.documents_models import Document, DocumentPublic
from src.modules.users.users_models import User
from sqlalchemy.orm import Session
from src.modules.companies.companies_models import Company
from src.core.models.http_responses import CommonHttpResponse
from src.modules.documents.documents_service import DocumentsService
from src.modules.documents.embeddings_service import EmbeddingService
from src.modules.documents.tenant_data_service import TenantDataService
import asyncio


class DocumentsController:
    def __init__(
        self, 
        http_service: HttpService, 
        s3_service: S3Service, 
        documents_service: DocumentsService, 
        embeddings_service: EmbeddingService,
        tenant_data_service: TenantDataService
    ):
        self.__http_service = http_service
        self.__s3_service = s3_service
        self.__documents_service = documents_service
        self.__embeddings_service = embeddings_service
        self.__tenant_data_service = tenant_data_service

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
        
        file_bytes = await self.__documents_service.read_file(file=file)

        s3_url = await self.__s3_service.upload(file_bytes=file_bytes, filename=file.filename, company_id=company_resource.company_id, user_id=company_resource.user_id)

        new_document = self.__documents_service.create(db=db, company_id=company_resource.company_id, filename=file.filename, url=s3_url)

        if file.filename.endswith((".xlsx", ".xls", ".xlsm", ".xlsb", ".csv")):
            try:
                self.__tenant_data_service.create_table_from_file(
                    db=db,
                    company_id=company_resource.company_id,
                    document_id=new_document.document_id,
                    filename=file.filename,
                    file_bytes=file_bytes
                )
            except:
                raise HTTPException(status_code=400, detail="Unsupported document type")
        else: 
            asyncio.create_task(
                self.__embeddings_service.add_document(
                    file_bytes=file_bytes,
                    filename=file.filename, 
                    user_id=user.user_id, 
                    company_id=company_resource.company_id
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

        data = self.__documents_service.collection(db=db, company_id=company_resource.company_id)

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

        self.__s3_service.delete_document_data(user_id=document_resource.company.user_id, company_id=document_resource.company_id, filename=document_resource.filename)
        
        self.__embeddings_service.delete_document_data(
            user_id=user.user_id,
            company_id=document_resource.company_id,
            filename=document_resource.filename
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

