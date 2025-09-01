from src.modules.documents.s3_service import S3Service
from src.modules.documents.documents_controller import DocumentsController
from src.modules.documents.documents_service import DocumentsService
from src.modules.documents.documents_models import Document
from src.core.repository.base_repository import BaseRepository
from src.core.services.http_service import HttpService
from src.core.services.data_handling_service import DataHandlingService
from src.core.dependencies.container import Container
from src.modules.documents.embeddings_service import EmbeddingService


def configure_documents_dependencies(http_service: HttpService, data_handler: DataHandlingService, s3_service: S3Service, embeddings_service: EmbeddingService):
    repository = BaseRepository(Document)

    service = DocumentsService(
        respository=repository,
        data_hander=data_handler
    )


    controller = DocumentsController(
        http_service=http_service,
        s3_service=s3_service,
        documents_service=service,
        embeddings_service=embeddings_service
    )

    Container.register("documents_service", service)
    Container.register("documents_controller", controller)