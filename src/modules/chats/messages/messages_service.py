from src.modules.chats.messages.messages_models import Message, MessageCreate
from src.core.repository.base_repository import BaseRepository
from src.core.logs.logger import Logger
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from uuid import UUID
from src.core.decorators.service_error_handler import service_error_handler
from operator import attrgetter
from src.core.dependencies.container import Container


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
    def collection(self, db: Session, chat_id: UUID) -> List[Message]:
        result = self._repository.get_many(db=db, key="chat_id", value=chat_id)
        if len(result) != 0:
            return sorted(result, key=attrgetter("created_at"), reverse=True)
        return []
    
    @service_error_handler(f"{__MODULE}.delete")
    def delete(self, db: Session, message_id: UUID)-> Message:
        return self._repository.delete(db=db, key="message_id", value=message_id)
    
    # async def handle_messages(self, db: Session, chat_id: UUID, human_message: str, ai_message: str, num_of_messages: int = 12): 
    #     redis_service: RedisService = Container.resolve("redis_service")
    #     incoming_message = MessageCreate(
    #         chat_id=chat_id,
    #         sender="human",
    #         text=human_message
    #     )

    #     outgoing_message = MessageCreate(
    #         chat_id=chat_id,
    #         sender="ai",
    #         text=ai_message
    #     )

    #     session_key = redis_service.get_agent_state_key(chat_id=chat_id)
    #     session = await redis_service.get_session(session_key)
    #     chat_history = session.get("chat_history", [])

    #     chat_history.insert(0, incoming_message.model_dump(exclude="chat_id"))
    #     if len(chat_history) > num_of_messages:
    #         chat_history.pop()  

    #     chat_history.insert(0, outgoing_message.model_dump(exclude="chat_id"))
    #     if len(chat_history) > num_of_messages:
    #         chat_history.pop()  
        
    #     self.create_many(db=db, messages=[incoming_message, outgoing_message])
        
    #     await redis_service.set_session(session_key, {
    #         "chat_history": chat_history
    #     }, expire_seconds=7200) #2 hours 
    
    
    