from fastapi import Depends
import boto3
import os

from src.modules.documents.interface.documents_controller import DocumentsController
from src.modules.documents.application.documents_service import DocumentsService
from src.core.services.encryption_service import EncryptionService
from  src.core.dependencies.services import get_encryption_service
from src.core.services.encryption_service import EncryptionService


from src.core.domain.repositories.vector_respository import VectorRepository
from src.core.domain.services.embedding_service import EmbeddingService
from src.core.infrastructure.services.embedding.openai_embedding_service import OpenAIEmbeddingService 
from src.core.infrastructure.repositories.vector.qdrant_vector_repository import QdrantVectorStore, get_qdrant_client
from src.core.domain.repositories.file_repository import FileRepository
from  src.core.infrastructure.repositories.file.s3_file_repository import S3FileRepository, get_s3_client
from src.core.domain.repositories.data_repository import DataRepository

from src.modules.documents.application.documents_service import DocumentsService
from src.modules.documents.application.tenant_data_service import TenantDataService
from src.modules.documents.infrastructure.sqlalchemy_documents_repository import SqlAlchemyDocumentsRepsoitory
from src.modules.documents.infrastructure.sqlalchemy_tennent_tables_repository import SqlAlchemyTennentTableRepsoitory
from src.modules.documents.domain.tenant_tables_repository import TenentTablesRepository
from src.modules.documents.application.use_cases.delete_document import DeleteDocument
from src.modules.documents.application.use_cases.upload_document import UploadDocument



def get_embedding_service() -> EmbeddingService:
    return OpenAIEmbeddingService(
        api_key=os.getenv("OPENAI_API_KEY")
    )

def get_file_repository(
    client = Depends(get_s3_client)
) -> FileRepository:    
    return S3FileRepository(
        client=client,
        bucket_name=os.getenv('AWS_BUCKET_NAME')
    )


def get_vector_repository(
    client = Depends(get_qdrant_client)
) -> VectorRepository:
    
    return QdrantVectorStore(client)


def get_documents_repository() -> DataRepository:
    return SqlAlchemyDocumentsRepsoitory()



def get_tenant_table_repository() -> TenentTablesRepository:
    return SqlAlchemyTennentTableRepsoitory()



def get_documents_service(
    repository: DataRepository = Depends(get_documents_repository),
    encryption_service: EncryptionService = Depends(get_encryption_service)
) -> DocumentsService:
    return DocumentsService(
        respository=repository,
        encryption_service=encryption_service
    )


def get_tenant_data_service(
    repository: TenentTablesRepository = Depends(get_tenant_table_repository)
) -> TenantDataService:
    return TenantDataService(
        repository=repository
    )


def get_delete_document_use_case(
    file_repository: FileRepository = Depends(get_file_repository),
    vector_repository: VectorRepository = Depends(get_vector_repository),
    tenant_data_service: TenantDataService = Depends(get_tenant_data_service),
    documents_service: DocumentsService = Depends(get_documents_service),
) -> DeleteDocument:
    return DeleteDocument(
        vector_repository=vector_repository,
        file_repository=file_repository,
        documents_service=documents_service,
        tenant_data_service=tenant_data_service
    )



def get_upload_document_use_case(
    file_repository: FileRepository = Depends(get_file_repository),
    vector_repository: VectorRepository = Depends(get_vector_repository),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    tenant_data_service: TenantDataService = Depends(get_tenant_data_service),
    documents_service: DocumentsService = Depends(get_documents_service),
) -> UploadDocument:
    return UploadDocument(
        vector_repository=vector_repository,
        embedding_service=embedding_service,
        file_repository=file_repository,
        documents_service=documents_service,
        tenant_data_service=tenant_data_service
    )


def get_documents_controller(
        encryption_service: EncryptionService = Depends(get_encryption_service),
        documents_service: DocumentsService = Depends(get_documents_service),
        delete_document: DeleteDocument = Depends(get_delete_document_use_case)

) -> DocumentsController:
    return DocumentsController(
        encryption_service=encryption_service,
        documents_service=documents_service,
        delete_document=delete_document
    )