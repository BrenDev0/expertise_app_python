from src.core.services.encryption_service import EncryptionService
from src.core.services.hashing_service import HashingService
from src.core.services.webtoken_service import WebTokenService
from src.core.middleware.middleware_service import MiddlewareService

def get_encryption_service() -> EncryptionService:
    return EncryptionService()

def get_hashing_service() -> HashingService:
    return HashingService()

def get_middleware_service() -> MiddlewareService:
    return MiddlewareService()

def get_web_token_service() -> WebTokenService:
    return WebTokenService()

