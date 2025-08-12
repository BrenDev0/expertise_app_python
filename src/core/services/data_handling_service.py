from src.core.services.encryption_service import EncryptionService
from src.core.services.hashing_service import HashingService

class DataHandlingService:
    def __init__(
        self,
        encryption_service: EncryptionService,
        hashing_service: HashingService,
    ):
        self.encryption_service: EncryptionService = encryption_service
        self.hashing_service: HashingService = hashing_service