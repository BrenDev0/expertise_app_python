from fastapi import Request

from sqlalchemy.orm import Session
from typing import List
from uuid import UUID


from src.modules.chats.chats_models import Chat, ChatPublic
from src.modules.users.domain.entities import User
from src.modules.chats.chats_service import ChatsService
from src.modules.chats.chats_models import  Chat, ChatCreate, ChatUpdate
from src.core.domain.models.http_responses import CommonHttpResponse

from src.core.services.request_validation_service import RequestValidationService



class ChatsController:
    def __init__(self, chats_service: ChatsService):
        self.__chats_service = chats_service

    def create_request(
        self, 
        req: Request, 
        data: ChatCreate,
        db: Session
    ) -> ChatPublic:
        user: User = req.state.user

        chat: Chat = self.__chats_service.create(
            db=db, 
            title=data.title, 
            user_id=user.user_id
        )
        
        return self.__to_public(chat)
 
    def collection_request(
        self, 
        req: Request, 
        db: Session
    ) -> List[ChatPublic]:
        user: User = req.state.user

        data = self.__chats_service.collection(db=db, user_id=user.user_id)
        
        return [self.__to_public(chat) for chat in data]

    def update_request(
        self, 
        chat_id: UUID,
        req: Request, 
        db: Session, 
        data: ChatUpdate, 
    ) -> CommonHttpResponse:
        user: User = req.state.user

        chat_resource: Chat = self.__chats_service.resource(
            db=db,
            key="chat_id",
            value=chat_id
        )

        RequestValidationService.verify_resource(
            result=chat_resource,
            not_found_message="Chat not found"
        )

        RequestValidationService.verifiy_ownership(user.user_id, chat_resource.user_id) 

        self.__chats_service.update(db=db, chat_id=chat_resource.chat_id, changes=data)

        return CommonHttpResponse(
            detail="Chat updated"
        )
    

    def delete_request(
        self,
        chat_id: UUID,
        req: Request,
        db: Session
    ):
        user: User = req.state.user

        chat_resource: Chat = self.__chats_service.resource(
            db=db, 
            key="chat_id",
            value=chat_id
        ) 

        RequestValidationService.verify_resource(
            result=chat_resource,
            not_found_message="Chat not found"
        )

        RequestValidationService.verifiy_ownership(user.user_id, chat_resource.user_id) 

        self.__chats_service.delete(db=db, chat_id=chat_resource.chat_id)

        return CommonHttpResponse(
            detail="Chat deleted"
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
        