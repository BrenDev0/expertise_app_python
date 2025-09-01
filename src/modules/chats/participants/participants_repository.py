from src.core.repository.base_repository import BaseRepository
from src.modules.chats.participants.participants_models import Participant
from sqlalchemy.orm import Session
from uuid import UUID
from sqlalchemy import select, delete

class ParticipantsRepository(BaseRepository):
    def __init__(self):
        super().__init__(Participant)

    def resource(self, db: Session, chat_id: UUID, agent_id: UUID) -> Participant | None:
        stmt = select(self.model).where(
            (self.model.chat_id == chat_id) &
            (self.model.agent_id == agent_id)
        )

        return db.execute(stmt).scalar_one_or_none()
    

    def delete_participant(self, db: Session, chat_id: UUID, agent_id: UUID) -> Participant:
        stmt = delete(self.model).where(
            (self.model.chat_id == chat_id) &
            (self.model.agent_id == agent_id)
        )

        result = db.execute(stmt)

        db.commit()
        deleted_row = result.fetchone()
        
        
        deleted_user = self.model(**deleted_row._mapping)
        return deleted_user