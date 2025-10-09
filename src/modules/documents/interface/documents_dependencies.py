from fastapi import Depends
import boto3
import os

from src.modules.documents.interface.documents_controller import DocumentsController
from src.modules.documents.application.documents_service import DocumentsService
from src.core.services.encryption_service import EncryptionService
from  src.core.dependencies.services import get_encryption_service
from src.core.services.encryption_service import EncryptionService


from src.core.domain.repositories.vector_respository import VectorRepository
from src.core.infrastructure.repositories.vector.qdrant_vector_repository import QdrantVectorStore
from src.core.domain.repositories.file_repository import FileRepository
from  src.core.infrastructure.repositories.file.s3_file_repository import S3FileRepository
from src.core.domain.repositories.data_repository import DataRepository

from src.modules.documents.application.documents_service import DocumentsService
from src.modules.documents.application.tenant_data_service import TenantDataService
from src.modules.documents.infrastructure.sqlalchemy_documents_repository import SqlAlchemyDocumentsRepsoitory
from src.modules.documents.infrastructure.sqlalchemy_tennent_tables_repository import SqlAlchemyTennentTableRepsoitory
from src.modules.documents.domain.tenant_tables_repository import TenentTablesRepository
from src.modules.documents.application.use_cases.delete_document import DeleteDocument



def get_file_repository() -> FileRepository:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )

    bucket_name = os.getenv('AWS_BUCKET_NAME')
    
    return S3FileRepository(
        client=s3_client,
        bucket_name=bucket_name
    )

def get_vector_repository() -> VectorRepository:
    from qdrant_client import QdrantClient
    qdrant_client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )
    return QdrantVectorStore(qdrant_client)

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
        tenent_data_service=tenant_data_service
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