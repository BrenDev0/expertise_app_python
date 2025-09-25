from fastapi import Depends

from src.core.services.data_handling_service import DataHandlingService
from src.core.services.email_service import EmailService
from src.core.services.encryption_service import EncryptionService
from src.core.services.hashing_service import HashingService
from src.core.services.http_service import HttpService
from src.core.services.redis_service import RedisService
from src.core.services.request_validation_service import RequestValidationService
from src.core.services.webtoken_service import WebTokenService
from src.core.middleware.middleware_service import MiddlewareService




## INDEPENDENT
def get_email_service() -> EmailService:
    return EmailService()

def get_encryption_service() -> EncryptionService:
    return EncryptionService()

def get_hashing_service() -> HashingService:
    return HashingService()

def get_redis_service() -> RedisService:
    return RedisService()

def get_request_validation_service() -> RequestValidationService:
    return RequestValidationService()

def get_web_token_service() -> WebTokenService:
    return WebTokenService()

## DEPENDANT
def get_data_hanlder(
    encryption_service: EncryptionService = Depends(get_encryption_service)
) -> DataHandlingService:
    return DataHandlingService()

def get_http_service(
    encryption_service: EncryptionService = Depends(get_encryption_service),
    hashing_service: HashingService = Depends(get_hashing_service),
    request_validation_service: RequestValidationService = Depends(get_request_validation_service),
    webtoken_service: WebTokenService = Depends(get_web_token_service)
) -> HttpService:
    return HttpService(
        encryption_service=encryption_service,
        hashing_service=hashing_service,
        request_validation_service=request_validation_service,
        webtoken_service=webtoken_service
    )

def get_middleware_service(
    http_service: HttpService = Depends(get_http_service)
):
    return MiddlewareService(
        http_service=http_service
    )

