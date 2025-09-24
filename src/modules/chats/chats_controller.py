from src.modules.chats.chats_models import Chat, ChatPublic
from src.modules.users.users_models import User
from src.modules.chats.chats_service import ChatsService
from src.modules.chats.chats_models import  Chat, ChatCreate, ChatCreateResponse, ChatUpdate
from src.core.models.http_responses import CommonHttpResponse
from fastapi import Request, HTTPException
from src.core.services.http_service import HttpService
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from src.modules.users.users_models import User
from src.modules.agents.agents_models import Agent
from src.modules.employees.employees_models import Employee
from src.modules.chats.participants.participants_service import ParticipantsService


class ChatsController:
    def __init__(self, http_service: HttpService, chats_service: ChatsService, participants_service: ParticipantsService):
        self.__http_service: HttpService = http_service
        self.__chats_service = chats_service
        self.__participants_service = participants_service

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

        chat_resource: Chat = self.__http_service.request_validation_service.verify_resource(
            service_key="chats_service",
            params={"db": db, "chat_id": chat_id},
            not_found_message="Chat not found"
        )  

        self.__http_service.request_validation_service.validate_action_authorization(user.user_id, chat_resource.user_id) 

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

        chat_resource: Chat = self.__http_service.request_validation_service.verify_resource(
            service_key="chats_service",
            params={"db": db, "chat_id": chat_id},
            not_found_message="Chat not found"
        )  

        self.__http_service.request_validation_service.validate_action_authorization(user.user_id, chat_resource.user_id) 

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
        