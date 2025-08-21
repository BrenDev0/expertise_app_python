from src.modules.chats.messages.messages_models import Message, MessageCreate
from src.core.repository.base_repository import BaseRepository
from typing import List
from sqlalchemy.orm import Session
from uuid import UUID
from src.core.decorators.service_error_handler import service_error_handler
from operator import attrgetter
from src.core.dependencies.container import Container
from src.core.services.redis_service import RedisService


class MessagesService():
    __MODULE = "messages.service"
    def __init__(self, repository: BaseRepository):
        self._repository = repository

    @service_error_handler(f"{__MODULE}.create")
    def create(self, db: Session,  message: MessageCreate) -> Message:
        return self._repository.create(db=db, data=Message(**message.model_dump(by_alias=False)))

    @service_error_handler(f"{__MODULE}.resource")
    def resource(self, db: Session, message_id: UUID) -> Message | None:
        return self._repository.get_one(db=db, key="chat_id", value=message_id)
    
    @service_error_handler(f"{__MODULE}.collection")
    def collection(self, db: Session, chat_id: UUID, num_of_messages: int = 50) -> List[Message]:
        return self._repository.get_many(
            db=db, 
            key="chat_id", 
            value=chat_id, 
            limit=num_of_messages, 
            order_by="created_at",
            desc=True
        )
    
    @service_error_handler(f"{__MODULE}.delete")
    def delete(self, db: Session, message_id: UUID)-> Message:
        return self._repository.delete(db=db, key="message_id", value=message_id)
    
    @service_error_handler(f"{__MODULE}.hanlde_messages")
    async def handle_messages(self, db: Session, chat_id: UUID, human_message: str, ai_message: str)-> tuple[MessageCreate, MessageCreate]:     
        incoming_message = MessageCreate(
            chat_id=chat_id,
            sender="human",
            text=human_message
        )

        self.create(db=db, message=incoming_message)
        
        outgoing_message = MessageCreate(
            chat_id=chat_id,
            sender="ai",
            text=ai_message
        )

        self.create(db=db, message=outgoing_message)
        
        return incoming_message, outgoing_message
    
    @service_error_handler(f"{__MODULE}.get_chat_history")
    def get_chat_history(self, db: Session, chat_id: UUID, num_of_messages: int = 12) -> List[Message]:
        return self.collection(db=db, chat_id=chat_id, num_of_messages=num_of_messages)

    