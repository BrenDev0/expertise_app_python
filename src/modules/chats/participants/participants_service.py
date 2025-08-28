from src.modules.chats.participants.participants_models import Participant
from src.core.repository.base_repository import BaseRepository

class ParticipantsService:
    def __init__(self, repository: BaseRepository):
        self.__repository = repository

    
        