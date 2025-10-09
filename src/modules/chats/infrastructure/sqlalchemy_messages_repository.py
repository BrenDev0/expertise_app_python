from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func, JSON, select, or_, and_, cast
import uuid
from sqlalchemy.dialects.postgresql import UUID
from typing import List

from src.modules.chats.domain.entities import Message
from src.modules.chats.domain.messages_repository import MessagesRepository
from src.modules.chats.infrastructure.sqlalchemy_chats_repository import SqlAlchemyChat
from src.core.infrastructure.repositories.data.sqlalchemy_data_repository import SqlAlchemyDataRepository, Base


class SqlAlchemyMessage(Base):
    __tablename__ = "messages"
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.chat_id", ondelete="CASCADE"), nullable=False)
    sender = Column(UUID(as_uuid=True), nullable=False) # can be user_id or agent_id depending on message_type 
    text = Column(Text, nullable=True)
    json_data = Column(JSON, nullable=True)
    message_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class SqlAlchemyMessagesRepository(SqlAlchemyDataRepository[Message, SqlAlchemyMessage], MessagesRepository):
    def __init__(self):
        super().__init__(SqlAlchemyMessage)

    def _to_entity(self, model: SqlAlchemyMessage) -> Message:
        return Message(
            message_id=model.message_id,
            chat_id=model.chat_id,
            sender=model.sender,
            text=model.text,
            json_data=model.json_data,
            message_type=model.message_type,
            created_at=model.created_at
        )
    
    def _to_model(self, entity: Message) -> SqlAlchemyMessage:
        data = entity.model_dump(exclude={'message_id', 'created_at'} if not entity.message_id else set())
        return SqlAlchemyMessage(**data)

    def search_by_content(
        self,
        content: str, 
        user_id: uuid.UUID
    ) -> List[Message]:
        stmt = select(SqlAlchemyMessage).join(SqlAlchemyChat).where(
            and_(
                SqlAlchemyChat.user_id == user_id,
                or_(
                    SqlAlchemyMessage.text.ilike(f'%{content}%'),
                    cast(SqlAlchemyMessage.json_data, String).ilike(f'%{content}%')
                )
            )
        )

        with self._get_session() as db:

            result = db.execute(stmt)

            search_results =  result.scalars().all()

            return [self._to_entity(msg) for msg in search_results] if search_results else []