from src.modules.chats.participants.participants_models import Participant
from src.core.repository.base_repository import BaseRepository
from sqlalchemy.orm import Session
from uuid import UUID
from src.core.decorators.service_error_handler import service_error_handler

class ParticipantsService:
    __MODULE = "participants.service"
    def __init__(self, repository: BaseRepository):
        self.__repository = repository

    @service_error_handler(module=__MODULE)
    def create(self, db: Session, agent_id: UUID, chat_id: UUID) -> Participant:
        participant = Participant(
            agent_id=agent_id,
            chat_id=chat_id
        )

        return self.__repository.create(db=db, data=participant)