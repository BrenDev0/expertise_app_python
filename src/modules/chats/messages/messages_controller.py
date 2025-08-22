from src.modules.chats.messages.messages_service import MessagesService
from src.modules.users.users_models import User
from src.modules.chats.messages.messages_models import Message, MessagePublic
from src.modules.chats.chats_models import  Chat
from fastapi import Request
from src.core.services.http_service import HttpService
from sqlalchemy.orm import Session
import uuid
from typing import List

class MessagesController:
    def __init__(self, http_service: HttpService, messages_service: MessagesService):
        self._http_service: HttpService = http_service
        self._messages_service = messages_service
        self._module = "messages.controller"
 
    def collection_request(
        self, 
        req: Request, 
        db: Session, 
        chat_id: uuid.UUID
    ) -> List[MessagePublic] :
        user: User = req.state.user

        chat_resource: Chat = self._http_service.request_validation_service.verify_resource(
            "chats_service",
            {"db": db, "chat_id": chat_id},
            not_found_message="Chat not found"
        )
    
        self._http_service.request_validation_service.validate_action_authorization(user.user_id, chat_resource.user_id)
        
        data = self._messages_service.collection(db=db, chat_id=chat_resource.chat_id)

        return [self.__to_public(message) for message in data]
        
   
    @staticmethod
    def __to_public(message: Message) -> MessagePublic:
        return MessagePublic.model_validate(message, from_attributes=True)