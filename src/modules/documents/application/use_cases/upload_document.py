from uuid import UUID
import logging
logger = logging.getLogger(__name__)

from src.modules.documents.application.documents_service import DocumentsService
from src.core.domain.repositories.vector_respository import VectorRepository
from src.core.domain.repositories.file_repository import FileRepository
from src.modules.documents.application.tenant_data_service import TenantDataService
from src.core.domain.services.embedding_service import EmbeddingService, EmbeddingResult

class UploadDocument():
    def __init__(
        self,
        vector_repository: VectorRepository,
        embedding_service: EmbeddingService,
        file_repository: FileRepository,
        documents_service: DocumentsService,
        tenant_data_service: TenantDataService
    ):
        self.__vector_repository = vector_repository
        self.__embedding_service = embedding_service
        self.__file_repository = file_repository
        self.__documents_service = documents_service
        self.__tenant_data_service = tenant_data_service

    async def execute(
        self,
        content_type: str,
        filename: str,
        file_bytes: bytes,
        company_id: UUID,
        user_id: UUID
    ):

        s3_url = await self.__file_repository.upload(file_bytes=file_bytes, filename=filename, company_id=company_id, user_id=user_id)


        new_document = self.__documents_service.create( 
            company_id=company_id, 
            filename=filename, 
            file_type=content_type,
            url=s3_url
        )

        if filename.endswith((".xlsx", ".xls", ".xlsm", ".xlsb", ".csv")):
            self.__tenant_data_service.create_table_from_file(
                company_id=company_id,
                document_id=new_document.document_id,
                filename=filename,
                file_bytes=file_bytes
            )
            
        else: 
            embedding_result = await self.__embedding_service.embed_document(
                file_bytes=file_bytes,
                filename=filename,
                document_id = new_document.document_id,
                company_id=company_id,
                user_id=user_id
            )

            namespace = f"expertise_user_{user_id}_company_{company_id}"
            
            result = self.__vector_repository.store_embeddings(
                embeddings=embedding_result.embeddings,
                chunks=embedding_result.chunks,
                namespace=namespace,
                # Additional metadata
                document_id=str(new_document.document_id),
                filename=filename,
                company_id=str(company_id),
                user_id=str(user_id),
                file_type=content_type
            )
            
            logger.info(f"Stored {len(embedding_result.chunks)} chunks in Qdrant")
            logger.info(f"Result: {result}")

        return new_document
