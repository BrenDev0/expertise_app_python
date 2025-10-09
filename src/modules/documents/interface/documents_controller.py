from uuid import UUID
from fastapi import Request, UploadFile, HTTPException,BackgroundTasks

from src.core.services.encryption_service import EncryptionService
from src.core.interface.request_validation_service import RequestValidationService
from src.core.domain.models.http_responses import CommonHttpResponse

from src.modules.documents.domain.documents_models import  DocumentPublic
from src.modules.documents.domain.entities import Document
from src.modules.users.domain.entities import User
from src.modules.companies.domain.enitities import Company
from src.modules.documents.application.documents_service import DocumentsService
from src.modules.documents.application.use_cases.delete_document import DeleteDocument
from src.modules.documents.application.use_cases.upload_document import UploadDocument



class DocumentsController:
    def __init__(
        self, 
        encryption_service: EncryptionService,
        documents_service: DocumentsService,
        delete_document: DeleteDocument
    ):
        self.__encryption_service = encryption_service
        self.__documents_service = documents_service
        self.__delete_document = delete_document
    

    async def upload_request(
        self,
        background_tasks: BackgroundTasks,
        req: Request,
        file: UploadFile,
        upload_document: UploadDocument
    ):
        user: User = req.state.user
        company: Company = req.state.company

        filename = file.filename.lower().replace(" ", "_")
        file_type = file.content_type
        file_bytes = await file.read()

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

        background_tasks.add_task(
            upload_document.execute,
            file_type,
            filename,
            file_bytes,
            company.company_id,
            user.user_id
        )
    
        return CommonHttpResponse(
            detail="file uploaded"
        )        
    

    def collection_request(
        self, 
        req: Request
    ):
        user: User = req.state.user
        company: Company = req.state.company


        RequestValidationService.verifiy_ownership(user.user_id, company.user_id)

        data = self.__documents_service.collection(company_id=company.company_id)

        return [
            self.__to_public(doc) for doc in data
        ]
    
    def delete_request(
        self,
        document_id: UUID,
        req: Request,
    ) ->  CommonHttpResponse:
        user: User = req.state.user
        company: Company = req.state.company

        document_resource: Document = self.__documents_service.resource(
            key="document_id",
            value=document_id
        )

        RequestValidationService.verify_resource(
            result=document_resource,
            not_found_message="Document not found"
        )
        

        RequestValidationService.verifiy_ownership(user.user_id, document_resource.company.user_id)

        self.__delete_document.execute(
            document_id=document_resource.document_id,
            company_id=company.company_id,
            user_id=company.user_id,
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
            file_type=data.file_type,
            url=self.__encryption_service.decrypt(data.url),
            uploaded_at=data.uploaded_at
        )

        return document

