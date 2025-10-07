from uuid import UUID
from sqlalchemy import select, or_, and_, cast, String
from sqlalchemy.orm import Session

from src.core.repository.base_repository import BaseRepository

from src.modules.chats.messages.messages_models import Message
from src.modules.chats.chats_models import Chat

class MessagesRepository(BaseRepository):
    def __init__(self):
        super().__init__(Message)

    def search_by_content(
        self,
        db: Session,
        content: str, 
        user_id: UUID
    ):
        stmt = select(Message).join(Chat).where(
            and_(
                Chat.user_id == user_id,
                or_(
                    Message.text.ilike(f'%{content}%'),
                    cast(Message.json_data, String).ilike(f'%{content}%')
                )
            )
        )

        result = db.execute(stmt)

        return result.scalars().all()
