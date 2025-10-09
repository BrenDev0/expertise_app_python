from src.core.dependencies.container import Container
from src.core.services.data_handling_service import DataHandlingService
from src.core.services.email_service import EmailService
from src.core.services.encryption_service import EncryptionService
from src.core.services.hashing_service import HashingService
from src.core.services.http_service import HttpService
from src.core.utils.logs.logger import Logger

from src.core.services.request_validation_service import RequestValidationService
from src.core.services.webtoken_service import WebTokenService
from src.core.services.redis_service import RedisService
import boto3
import os





def configure_container():
    ## core ##   
    
    # Independent #
    email_service = EmailService()
    Container.register("email_service", email_service)

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
    
    # multi domain # must configure single domain dependencies above this line #
   
    ## multi server dependencies ##


