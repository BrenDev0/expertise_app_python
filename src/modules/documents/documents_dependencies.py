import boto3
import os
from src.modules.documents.s3_service import S3Service
from src.modules.documents.documents_controller import DocumentsController
from src.modules.documents.documents_service import DocumentsService
from src.modules.documents.documents_models import Document
from src.core.repository.base_repository import BaseRepository
from src.core.services.http_service import HttpService
from src.core.services.data_handling_service import DataHandlingService
from src.core.dependencies.container import Container


def configure_documents_dependencies(http_service: HttpService, data_handler: DataHandlingService):
    client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
    
    bucket_name = os.getenv('S3_BUCKET_NAME')

    s3_service = S3Service(
        client=client,
        bucket_name=bucket_name
    )

    repository = BaseRepository(Document)

    service = DocumentsService(
        respository=repository,
        data_hander=data_handler
    )

    controller = DocumentsController(
        http_service=http_service,
        s3_service=s3_service,
        documents_service=service
    )

    Container.register("documents_service", service)
    Container.register("documents_controller", controller)