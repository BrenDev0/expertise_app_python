from src.modules.documents.s3_service import S3Service
from src.modules.documents.documents_controller import DocumentsController
from src.modules.documents.documents_service import DocumentsService
from src.modules.documents.documents_models import Document, TenantTable
from src.core.repository.base_repository import BaseRepository
from src.core.services.http_service import HttpService
from src.core.services.data_handling_service import DataHandlingService
from src.core.dependencies.container import Container
from src.modules.documents.embeddings_service import EmbeddingService
from src.modules.documents.tenant_data_service import TenantDataService
from src.modules.documents.document_manager import DocumentManager


def configure_documents_dependencies(
    http_service: HttpService, 
    data_handler: DataHandlingService, 
    s3_service: S3Service, 
    embeddings_service: EmbeddingService
):
    repository = BaseRepository(Document)
    tenant_repository = BaseRepository(TenantTable)

    service = DocumentsService(
        respository=repository,
        data_hander=data_handler
    )

    tenant_data_service = TenantDataService(
        repository=tenant_repository
    )

    document_manager = DocumentManager(
        documents_service=service,
        embedding_service=embeddings_service,
        s3_service=s3_service,
        tenant_data_service=tenant_data_service
    )


    controller = DocumentsController(
        http_service=http_service,
        document_manager=document_manager
    )

    Container.register("documents_service", service)
    Container.register("documents_controller", controller)
    Container.register("document_manager", document_manager)