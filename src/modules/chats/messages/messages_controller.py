from src.modules.chats.messages.messages_service import MessagesService
from src.modules.users.users_models import User
from src.modules.chats.messages.messages_models import Message, MessagePublic, MessageCreate
from src.modules.chats.chats_models import  Chat
from fastapi import Request
from src.core.models.http_responses import CommonHttpResponse
from src.core.services.http_service import HttpService
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from src.core.dependencies.container import Container
from src.modules.state.state_service import StateService
import asyncio

class MessagesController:
    def __init__(self, http_service: HttpService, messages_service: MessagesService):
        self.__http_service: HttpService = http_service
        self.__messages_service = messages_service
 
    async def create_request(
        self,
        chat_id: UUID,
        data: MessageCreate,
        db: Session
    ) -> CommonHttpResponse:
        chat_resource: Chat = self.__http_service.request_validation_service.verify_resource(
            service_key="chats_service",
            params={
                "db": db,
                "chat_id": chat_id
            },
            not_found_message="Chat not found"
        )

        if data.message_type == "human":
            self.__http_service.request_validation_service.validate_action_authorization(chat_resource.user_id, data.sender)
        
        message = self.__messages_service.create(
            db=db, 
            chat_id=chat_resource.chat_id, 
            sender_id=data.sender, 
            message_type=data.message_type, 
            text=str(data.text)
        )


        ## handle state if exists
        state_service: StateService = Container.resolve("state_service")
        asyncio.create_task(
            state_service.update_chat_state_history(
                chat_resource.chat_id, 
                message,
                16
            )
        )

        return CommonHttpResponse(
            detail="Message created"
        )

    def collection_request(
        self, 
        req: Request, 
        db: Session, 
        chat_id: UUID
    ) -> List[MessagePublic] :
        user: User = req.state.user

        chat_resource: Chat = self.__http_service.request_validation_service.verify_resource(
            "chats_service",
            {"db": db, "chat_id": chat_id},
            not_found_message="Chat not found"
        )
    
        self.__http_service.request_validation_service.validate_action_authorization(user.user_id, chat_resource.user_id)
        
        data = self.__messages_service.collection(db=db, chat_id=chat_resource.chat_id)

        return [self.__to_public(message) for message in data]
        
   
    @staticmethod
    def __to_public(message: Message) -> MessagePublic:
        return MessagePublic.model_validate(message, from_attributes=True)