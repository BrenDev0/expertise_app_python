from src.modules.documents.documents_service import DocumentsService
from src.modules.documents.embeddings_service import EmbeddingService
from src.modules.documents.s3_service import S3Service
from src.modules.documents.tenant_data_service import TenantDataService
from src.core.decorators.service_error_handler import service_error_handler
from fastapi import UploadFile
from  uuid import UUID
from sqlalchemy.orm import Session
from src.modules.documents.documents_models import Document
from src.core.dependencies.container import Container
from src.modules.companies.companies_service import CompaniesService
from src.modules.companies.companies_models import Company

class DocumentManager:
    __MODULE = "documents.manager"
    def __init__(
        self, 
        documents_service: DocumentsService,
        embedding_service: EmbeddingService,
        s3_service: S3Service,
        tenant_data_service: TenantDataService
    ):
        self.documents_service = documents_service
        self.__embedding_service = embedding_service
        self.__s3_service = s3_service
        self.__tenant_data_service = tenant_data_service


    @service_error_handler(module=__MODULE)
    async def handle_upload(
        self,
        file: UploadFile,
        company_id: UUID,
        user_id: UUID,
        db: Session
    ):
        filename = file.filename.lower().replace(" ", "_")
        
        file_bytes = await file.read()

        s3_url = await self.__s3_service.upload(file_bytes=file_bytes, filename=filename, company_id=company_id, user_id=user_id)

        new_document: Document = self.documents_service.create(db=db, company_id=company_id, filename=filename, url=s3_url)

        if filename.endswith((".xlsx", ".xls", ".xlsm", ".xlsb", ".csv")):
            self.__tenant_data_service.create_table_from_file(
                db=db,
                company_id=company_id,
                document_id=new_document.document_id,
                filename=filename,
                file_bytes=file_bytes
            )
            
        else: 
            await self.__embedding_service.add_document(
                    file_bytes=file_bytes,
                    filename=filename, 
                    user_id=user_id, 
                    company_id=company_id
                )



    @service_error_handler(module=__MODULE)
    def document_level_deletion(
        self,
        document_id: UUID,
        company_id: UUID,
        user_id: UUID,
        filename: str,
        db: Session
    ):
        
        self.__s3_service.delete_document_data(
            user_id=user_id, 
            company_id=company_id, 
            filename=filename
        )
        
        if filename.endswith((".xlsx", ".xls", ".xlsm", ".xlsb", ".csv")):
            self.__tenant_data_service.delete_document_table(
                db=db,
                document_id=document_id
            )
        else:
            self.__embedding_service.delete_document_data(
                user_id=str(user_id),
                company_id=str(company_id),
                filename=filename
            )

        self.documents_service.delete(
            db=db,
            key="document_id",
            value=document_id
        )

    @service_error_handler(module=__MODULE)
    def company_level_deletion(
        self,
        company_id: UUID,
        user_id: UUID,
        db: Session
    ) -> str:
        self.__tenant_data_service.delete_companies_tables(
            db=db,
            company_id=company_id
        )

        self.__s3_service.delete_company_data(
            user_id=user_id,
            company_id=company_id
        )

        self.__embedding_service.delete_company_data(
            user_id=user_id,
            company_id=company_id
        )

        self.documents_service.delete(
            db=db,
            key="company_id",
            value=company_id
        )

        return "Company documents deleted"

    @service_error_handler(module=__MODULE)
    def user_level_deletion(
        self,
        user_id: UUID,
        db: Session
    ) -> str:
        companies_service: CompaniesService = Container.resolve("companies_service")
        users_companies = companies_service.collection(db=db, user_id=user_id)

        self.__s3_service.delete_user_data(user_id=user_id)

        self.__embedding_service.delete_user_data(user_id=user_id)

        for company in users_companies:
            self.__tenant_data_service.delete_companies_tables(
                db=db,
                company_id=company.company_id
            )

            self.documents_service.delete(
                db=db,
                key="company_id",
                value=company.company_id
            )

        return "User documents deleted"
