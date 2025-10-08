from src.modules.chats.messages.messages_service import MessagesService
from src.modules.users.domain.entities import User
from src.modules.chats.messages.messages_models import Message, MessagePublic, MessageCreate
from src.modules.chats.chats_models import  Chat
from fastapi import Request
from src.core.domain.models.http_responses import CommonHttpResponse
from src.core.services.http_service import HttpService
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from src.core.dependencies.container import Container
from src.modules.state.state_service import StateService
from src.modules.chats.chats_service import ChatsService
import asyncio
from src.core.services.request_validation_service import RequestValidationService

class MessagesController:
    def __init__(self, messages_service: MessagesService):
        self.__messages_service = messages_service
 
    async def create_request(
        self,
        chat_id: UUID,
        data: MessageCreate,
        chats_service: ChatsService,
        db: Session
    ) -> CommonHttpResponse:
        chat_resource: Chat = chats_service.resource(
            key="chat_id",
            value=chat_id
        )

        RequestValidationService.verify_resource(
            result=chat_resource,
            not_found_message="Chat not found"
        )

        if data.message_type == "human":
            RequestValidationService.verifiy_ownership(chat_resource.user_id, data.sender)
        
        message = self.__messages_service.create(
            db=db, 
            chat_id=chat_resource.chat_id, 
            sender_id=data.sender, 
            message_type=data.message_type, 
            text=data.text,
            json_data=data.json_data
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
        chat_id: UUID,
        req: Request,
        chats_service: ChatsService, 
        db: Session
    ) -> List[MessagePublic] :
        user: User = req.state.user

        chat_resource: Chat = chats_service.resource(
            key="chat_id",
            value=chat_id
        )

        RequestValidationService.verify_resource(
            result=chat_resource,
            not_found_message="Chat not found"
        )
    
        RequestValidationService.verifiy_ownership(user.user_id, chat_resource.user_id)
        
        data = self.__messages_service.collection(db=db, key="chat_id", value=chat_resource.chat_id)

        return [self.__to_public(message) for message in data]
    
    def search_request(
        self,
        req: Request,
        query: str,
        db: Session
    ) -> List[MessagePublic]:
        user: User = req.state.user

        data = self.__messages_service.query(
            db=db,
            content=query,
            user_id=user.user_id
        )

        return [self.__to_public(message) for message in data]

    @staticmethod
    def __to_public(message: Message) -> MessagePublic:
        return MessagePublic.model_validate(message, from_attributes=True)