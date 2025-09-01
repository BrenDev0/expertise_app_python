from src.core.services.http_service import HttpService
from src.modules.chats.participants.participants_service import ParticipantsService
from src.modules.chats.participants.participants_models import InviteToChat, RemoveFromChat
from src.core.models.http_responses import CommonHttpResponse
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import Request
from src.modules.users.users_models import User
from src.modules.employees.employees_models import Employee
from src.modules.agents.agents_models import Agent
from src.modules.chats.chats_models import Chat


class ParticipantsController:
    def __init__(self, http_service: HttpService, participants_service: ParticipantsService):
        self.__http_service = http_service
        self.__participants_service = participants_service

    def add_to_chat(
        self, 
        chat_id: UUID,
        req: Request,
        data: InviteToChat,
        db: Session
    ) -> CommonHttpResponse:
        user: User = req.state.user

        chat_resource: Chat = self.__http_service.request_validation_service.verify_resource(
            service_key="chats_service",
            params={
                "db": db,
                "chat_id": chat_id
            },
            not_found_message="Chat not found"
        )

        self.__http_service.request_validation_service.validate_action_authorization(user.user_id, chat_resource.user_id)

        for agent_id in data.agents:
            if not user.is_admin:
                employee_resource: Employee = self.__http_service.request_validation_service.verify_resource(
                    service_key="employees_service",
                    params={
                        "db": db,
                        "key": "user_id",
                        "value": user.user_id
                    },
                    not_found_message="Employee profile not found"
                )

                if not employee_resource.is_manager:
                    agent_resource: Agent = self.__http_service.request_validation_service.verify_resource(
                        service_key="agents_service",
                        params={
                            "db": db,
                            "agent_id": agent_id
                        },
                        not_found_message="Agent not found"
                    )

                    self.__http_service.request_validation_service.verify_resource(
                        service_key="agent_access_service",
                        params={
                            "db": db,
                            "user_id": user.user_id,
                            "agent_id": agent_resource.agent_id
                        },
                        not_found_message="User does not have access to agent",
                        status_code=403
                    )

            self.__participants_service.create(db=db, agent_id=agent_id, chat_id=chat_id)


    def remove_from_chat(
        self,
        chat_id: UUID,
        req: Request,
        data: RemoveFromChat,
        db: Session
    ):
        user: User = req.state.user

        chat_resource: Chat = self.__http_service.request_validation_service.verify_resource(
            service_key="chats_service",
            params={
                "db": db,
                "chat_id": chat_id
            },
            not_found_message="Chat not found"
        )

        self.__http_service.request_validation_service.validate_action_authorization(user.user_id, chat_resource.user_id)

        for agent_id in data.agents:
            participant_resource = self.__http_service.request_validation_service.verify_resource(
                service_key="participants_service",
                params={
                    "db": db,
                    "chat_id": chat_resource.chat_id,
                    "agent_id": agent_id 
                },
                throw_http_error=False
            )

            if participant_resource:
                self.__participants_service.delete(
                    db=db, 
                    chat_id=chat_resource.chat_id,
                    agent_id=agent_id
                )
        
        return CommonHttpResponse(
            detail="Agents removed from chat"
        )