from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

from  src.modules.chats.domain.entities import Chat

from src.core.infrastructure.repositories.data.sqlalchemy_data_repository import SqlAlchemyDataRepository, Base

class SqlAlchemyChat(Base):
    __tablename__ = "chats"
    chat_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=True)


class SqlAchemyChatsRepsitory(SqlAlchemyDataRepository[Chat, SqlAlchemyChat]):
    def __init__(self):
        super().__init__(SqlAlchemyChat)

    def _to_entity(self, model: SqlAlchemyChat) -> Chat:
        return Chat(
            chat_id=model.chat_id,
            user_id=model.user_id,
            title=model.title
        )
    
    def _to_model(self, entity: Chat) -> SqlAlchemyChat:
        data = entity.model_dump(exclude={'chat_id', 'created_at'} if not entity.chat_id else set())
        return SqlAlchemyChat(**data)