from typing import List, Any, Union
from uuid import UUID

from src.modules.chats.domain.entities import Message
from src.modules.chats.domain.messages_repository import MessagesRepository
from src.core.utils.decorators.service_error_handler import service_error_handler

class MessagesService():
    __MODULE = "messages.service"
    def __init__(self, repository: MessagesRepository):
        self.__repository = repository

    @service_error_handler(f"{__MODULE}.create")
    def create(
        self,
        chat_id: UUID, 
        sender_id: UUID, 
        message_type: UUID, 
        text: str = None,
        json_data: Any = None
    )-> Message:     
        message = Message(
            chat_id=chat_id,
            sender=sender_id,
            message_type=message_type,
            text=text,
            json_data=json_data
        )

        return self.__repository.create(data=message)

    @service_error_handler(module=__MODULE)
    def resource(self, message_id: UUID) -> Message | None:
        return self.__repository.get_one(key="chat_id", value=message_id)
    
    @service_error_handler(module=__MODULE)
    def collection(self, key: str, value: Union[UUID, str], num_of_messages: int = 50) -> List[Message]:
        return self.__repository.get_many(
            key=key, 
            value=value, 
            limit=num_of_messages, 
            order_by="created_at",
            desc=False
        )
    
    @service_error_handler(module=__MODULE)
    def delete(self, message_id: UUID)-> Message | None:
        return self.__repository.delete(key="message_id", value=message_id)
 

    @service_error_handler(module=__MODULE)
    def get_chat_history(self, chat_id: UUID, num_of_messages: int = 12) -> List[Message]:
        return self.collection(chat_id=chat_id, num_of_messages=num_of_messages)
    
    @service_error_handler(module=__MODULE)
    def query(self, content: str, user_id: UUID):
        return self.__repository.search_by_content(content=content, user_id=user_id)

    