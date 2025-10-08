from src.core.dependencies.container import Container
from src.core.services.data_handling_service import DataHandlingService
from src.core.services.email_service import EmailService
from src.core.services.encryption_service import EncryptionService
from src.core.services.hashing_service import HashingService
from src.core.services.http_service import HttpService
from src.core.utils.logs.logger import Logger
from src.core.middleware.middleware_service import MiddlewareService
from src.core.services.request_validation_service import RequestValidationService
from src.core.services.webtoken_service import WebTokenService
from src.core.services.redis_service import RedisService
import boto3
import os
from src.modules.documents.services.s3_service import S3Service
from qdrant_client import QdrantClient
from src.modules.documents.services.embeddings_service import EmbeddingService
from src.modules.chats.chats_dependencies import configure_chats_dependencies

from src.modules.invites.invites_dependencies import configure_invites_dependencies
from src.modules.documents.documents_dependencies import configure_documents_dependencies
from src.modules.employees.employees_dependencies import configure_employee_dependencies
from src.modules.agents.agents_dependencies import configure_agents_dependencies
from src.modules.interactions.interactions_dependencies import configure_interactions_dependencies
from src.modules.state.state_dependencies  import configure_state_dependencies

from src.modules.users.application.users_service import UsersService
from src.modules.users.infrastructure.sqlalchemy_user_repository import SqlAlchemyUsersRepository
from src.modules.users.application.use_cases.create_user import CreateUserUseCase
from src.modules.users.application.use_cases.update_user import UpdateUserUseCase


def configure_container():
    ## core ##   
    
    # Independent #
    email_service = EmailService()
    Container.register("email_service", email_service)

    qdrant_client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

    embeddings_service = EmbeddingService(client=qdrant_client)
    Container.register("embeddings_service", embeddings_service)

    encryption_service = EncryptionService()
    Container.register("encryption_service", encryption_service)

    hashing_service = HashingService()
    Container.register("hashing_service", hashing_service)

    logger = Logger()
    Container.register("logger", logger)

    redis_service = RedisService()
    Container.register("redis_service", redis_service)

    request_validation_service = RequestValidationService()
    Container.register("request_validation_service", request_validation_service)

    s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
    
    bucket_name = os.getenv('AWS_BUCKET_NAME')

    s3_service = S3Service(
        client=s3_client,
        bucket_name=bucket_name
    )
    Container.register("s3_service", s3_service)

    webtoken_service = WebTokenService()
    Container.register("webtoken_service", webtoken_service)


    # Dependent # Must configure all independent instances above this line #
    data_handler = DataHandlingService(
        encryption_service=encryption_service,
        hashing_service=hashing_service
    )
    Container.register("data_handler", data_handler)

    http_service = HttpService(
        encryption_service=encryption_service,
        hashing_service=hashing_service,
        request_validation_service=request_validation_service,
        webtoken_service=webtoken_service
    )
    Container.register("http_service", http_service)

 
    ## Module # Must configure core dependencies above this line ##

    # single domain # 
    configure_agents_dependencies(
        http_service=http_service
    )

    configure_chats_dependencies(
        http_service=http_service
    )

    configure_documents_dependencies(
        encrytption_service=encryption_service,
        data_handler=data_handler,
        s3_service=s3_service,
        embeddings_service=embeddings_service  
    )

    configure_invites_dependencies(
        http_service=http_service,
        data_handler=data_handler,
        email_service=email_service
    )


    

    users_service = UsersService(
        respository=SqlAlchemyUsersRepository(),
        create_user_use_case=CreateUserUseCase(
            encryption_service=encryption_service,
            hashing_service=hashing_service
        ),
        update_user_use_case=UpdateUserUseCase(
            encryption_service=encryption_service,
            hashing_service=hashing_service
        )
    )

    Container.register("users_service", users_service)

    
    # multi domain # must configure single domain dependencies above this line #
   

    configure_state_dependencies(redis_service=redis_service)

    ## multi server dependencies ##
    configure_interactions_dependencies(http_service=http_service)

