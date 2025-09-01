from src.modules.chats.participants.participants_models import Participant
from src.modules.chats.participants.participants_repository import ParticipantsRepository
from sqlalchemy.orm import Session
from uuid import UUID
from src.core.decorators.service_error_handler import service_error_handler

class ParticipantsService:
    __MODULE = "participants.service"
    def __init__(self, repository: ParticipantsRepository):
        self.__repository = repository

    @service_error_handler(module=__MODULE)
    def create(self, db: Session, agent_id: UUID, chat_id: UUID) -> Participant:
        participant = Participant(
            agent_id=agent_id,
            chat_id=chat_id
        )

        return self.__repository.create(db=db, data=participant)
    
    def resource(self, db: Session, chat_id: UUID, agent_id: UUID):
        return self.__repository.resource(db=db, chat_id=chat_id, agent_id=agent_id)

    def delete(self, db: Session, chat_id: UUID, agent_id: UUID):
        return self.__repository.delete_participant(db=db, chat_id=chat_id, agent_id=agent_id)