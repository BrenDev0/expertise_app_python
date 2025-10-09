from uuid import UUID
from typing import List
from fastapi import Request, BackgroundTasks
import asyncio

from src.core.services.request_validation_service import RequestValidationService
from src.core.domain.models.http_responses import CommonHttpResponse
from src.core.dependencies.container import Container

from src.modules.chats.application.messages_service import MessagesService
from src.modules.chats.domain.messages_models import MessagePublic, MessageCreate
from src.modules.chats.domain.entities import Chat, Message
from src.modules.users.domain.entities import User
from src.modules.state.application.state_service import StateService
from src.modules.chats.application.chats_service import ChatsService

class MessagesController:
    def __init__(
        self, 
        messages_service: MessagesService,
        chats_service: ChatsService
    ):
        self.__messages_service = messages_service
        self.__chats_service = chats_service
 
    async def create_request(
        self,
        background_tasks: BackgroundTasks,
        chat_id: UUID,
        data: MessageCreate,
        state_service: StateService
    ) -> CommonHttpResponse:
        chat_resource = self.__chats_service.resource(
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
            chat_id=chat_resource.chat_id, 
            sender_id=data.sender, 
            message_type=data.message_type, 
            text=data.text,
            json_data=data.json_data
        )

        ## handle state if exists in background
        background_tasks.add_task(state_service.update_chat_state_history, chat_resource.chat_id, message, 16)

        return CommonHttpResponse(
            detail="Message created"
        )

    def collection_request(
        self, 
        chat_id: UUID,
        req: Request
    ) -> List[MessagePublic] :
        user: User = req.state.user

        chat_resource = self.__chats_service.resource(
            key="chat_id",
            value=chat_id
        )

        RequestValidationService.verify_resource(
            result=chat_resource,
            not_found_message="Chat not found"
        )
    
        RequestValidationService.verifiy_ownership(user.user_id, chat_resource.user_id)
        
        data = self.__messages_service.collection(key="chat_id", value=chat_resource.chat_id)

        return [self.__to_public(message) for message in data]
    
    def search_request(
        self,
        req: Request,
        query: str
    ) -> List[MessagePublic]:
        user: User = req.state.user

        data = self.__messages_service.query(
            content=query,
            user_id=user.user_id
        )

        return [self.__to_public(message) for message in data]

    @staticmethod
    def __to_public(message: Message) -> MessagePublic:
        return MessagePublic.model_validate(message, from_attributes=True)