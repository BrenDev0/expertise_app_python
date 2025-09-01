from src.modules.chats.messages.messages_models import Message, MessageCreate
from src.core.repository.base_repository import BaseRepository
from typing import List
from sqlalchemy.orm import Session
from uuid import UUID
from src.core.decorators.service_error_handler import service_error_handler

class MessagesService():
    __MODULE = "messages.service"
    def __init__(self, repository: BaseRepository):
        self.__repository = repository

    @service_error_handler(f"{__MODULE}.create")
    def create(self, db: Session, chat_id: UUID, sender_id: UUID, message_type: UUID, text: str)-> Message:     
        message = MessageCreate(
            chat_id=chat_id,
            sender=sender_id,
            message_type=message_type,
            text=text
        )

        return self.__repository.create(db=db, data=message)

    @service_error_handler(f"{__MODULE}.resource")
    def resource(self, db: Session, message_id: UUID) -> Message | None:
        return self.__repository.get_one(db=db, key="chat_id", value=message_id)
    
    @service_error_handler(f"{__MODULE}.collection")
    def collection(self, db: Session, chat_id: UUID, num_of_messages: int = 50) -> List[Message]:
        return self.__repository.get_many(
            db=db, 
            key="chat_id", 
            value=chat_id, 
            limit=num_of_messages, 
            order_by="created_at",
            desc=True
        )
    
    @service_error_handler(f"{__MODULE}.delete")
    def delete(self, db: Session, message_id: UUID)-> Message:
        return self.__repository.delete(db=db, key="message_id", value=message_id)
 

    @service_error_handler(f"{__MODULE}.get_chat_history")
    def get_chat_history(self, db: Session, chat_id: UUID, num_of_messages: int = 12) -> List[Message]:
        return self.collection(db=db, chat_id=chat_id, num_of_messages=num_of_messages)

    