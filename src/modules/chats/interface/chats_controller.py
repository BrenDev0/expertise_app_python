from fastapi import Request, UploadFile
from typing import List
from uuid import UUID
import logging
logger = logging.getLogger(__name__)

from src.modules.chats.domain.entities import Chat
from src.modules.users.domain.entities import User
from src.modules.chats.application.chats_service import ChatsService
from src.modules.chats.domain.chats_models import ChatCreate, ChatUpdate, ChatPublic
from src.core.domain.models.http_responses import CommonHttpResponse
from src.modules.chats.application.chat_context_service import ChatContextService

from src.core.interface.request_validation_service import RequestValidationService



class ChatsController:
    def __init__(
        self, 
        chats_service: ChatsService,
        chat_context_service: ChatContextService
    ):
        self.__chats_service = chats_service
        self.__chat_context_service = chat_context_service

    def create_request(
        self, 
        req: Request, 
        data: ChatCreate
    ) -> ChatPublic:
        user: User = req.state.user

        chat: Chat = self.__chats_service.create( 
            title=data.title, 
            user_id=user.user_id
        )
        
        return self.__to_public(chat)
 
    def collection_request(
        self, 
        req: Request
    ) -> List[ChatPublic]:
        user: User = req.state.user

        data = self.__chats_service.collection(user_id=user.user_id)
        
        return [self.__to_public(chat) for chat in data]

    def update_request(
        self, 
        chat_id: UUID,
        req: Request, 
        data: ChatUpdate, 
    ) -> CommonHttpResponse:
        user: User = req.state.user

        chat_resource = self.__verify_chat_and_ownership(chat_id=chat_id, user=user)

        self.__chats_service.update(chat_id=chat_resource.chat_id, changes=data)

        return CommonHttpResponse(
            detail="Chat updated"
        )
    

    def delete_request(
        self,
        chat_id: UUID,
        req: Request
    ):
        user: User = req.state.user

        chat_resource = self.__verify_chat_and_ownership(chat_id=chat_id, user=user)

        self.__chats_service.delete(chat_id=chat_resource.chat_id)

        return CommonHttpResponse(
            detail="Chat deleted"
        )
   


    async def add_context(
        self,
        chat_id: UUID,
        req: Request,
        file: UploadFile,
    ) -> CommonHttpResponse:
        user: User = req.state.user

        chat_resource = self.__verify_chat_and_ownership(chat_id=chat_id, user=user)
        logger.debug(file.filename)
        filename = file.filename.lower().replace(" ", "_")
        file_bytes = await file.read()
        
        await self.__chat_context_service.add_context(
            file_bytes=file_bytes,
            filename=filename,
            chat_id=chat_resource.chat_id
        )

        return CommonHttpResponse(
            detail="context added"
        )
    
    def remove_context(
        self,
        req: Request,
        chat_id: UUID,
        filename: str
    ) -> CommonHttpResponse:
        user: User = req.state.user

        chat_resource = self.__verify_chat_and_ownership(chat_id=chat_id, user=user)

        cleaned_filename = filename.lower().replace(" ", "_")
        self.__chat_context_service.remove_context(
            chat_id=chat_resource.chat_id,
            filename=cleaned_filename
        )

        return CommonHttpResponse(
            detail="context removed"
        )

    @staticmethod
    def __to_public(chat: Chat) -> ChatPublic:
        return ChatPublic.model_validate(
            {
                "chat_id": chat.chat_id,
                "user_id": chat.user_id,
                "title": chat.title
            }
        )

    def __verify_chat_and_ownership(self, chat_id: UUID, user: User) -> Chat:
        chat_resource: Chat = self.__chats_service.resource(
            key="chat_id",
            value=chat_id
        ) 

        RequestValidationService.verify_resource(
            result=chat_resource,
            not_found_message="Chat not found"
        )

        RequestValidationService.verifiy_ownership(user.user_id, chat_resource.user_id) 

        return chat_resource