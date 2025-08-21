from src.modules.state.state_models import ChatState
from src.core.models.http_responses import CommonHttpResponse
from src.core.services.http_service import HttpService
from src.modules.interactions.interactions_models import InteractionRequest
from src.modules.state.state_service import StateService
from fastapi import Request, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID
from src.modules.users.users_models import User
from src.modules.chats.chats_models import Chat

class InteractionsController:
    def __init__(
        self, 
        http_service: HttpService, 
        state_service: StateService
    ):
        self.__http_service = http_service
        self.__state_service = state_service

    def incoming_interaction(
        self,
        agent_id: UUID,
        req: Request,
        data: InteractionRequest,
        db: Session,
        backrgound_tasks: BackgroundTasks
    ): 
        user: User = req.state.user

        chat_resource: Chat = self.__http_service.request_validation_service.verify_resource(
            service_key="chats_service",
            params={
                "db": db,
                "chat_id": data.chat_id
            },
            not_found_message="Chat not found"
        )

        self.__http_service.request_validation_service.validate_action_authorization(user.user_id, chat_resource.user_id)
        self.__http_service.request_validation_service.validate_action_authorization(agent_id, chat_resource.agent_id)
        
        chat_state = self.__state_service.ensure_chat_state(
            db=db,
            chat_id=chat_resource.chat_id,
            input=data.input,
            user_id=user.user_id,
            agent_id=agent_id
        )

        # backrgound_tasks.add_task(self.__interactions_service.send_to_agent, chat_state)

        return CommonHttpResponse(
            detail="Request sent to agent"
        )

    def outgoing_interaction():
        pass
        