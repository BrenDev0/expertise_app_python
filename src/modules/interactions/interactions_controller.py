from src.modules.state.state_models import ChatState
from src.core.models.http_responses import CommonHttpResponse
from src.core.services.http_service import HttpService
from src.modules.interactions.interactions_models import HumanToAgentRequest, AgentToHumanRequest
from src.modules.interactions.interactions_service import InteractionsService
from src.modules.chats.messages.messages_service import MessagesService
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
        interactions_service: InteractionsService,
        messaging_service: MessagesService,
        state_service: StateService
    ):
        self.__http_service = http_service
        self.__interactions_service = interactions_service
        self.__messages_service = messaging_service
        self.__state_service = state_service

    async def incoming_interaction(
        self,
        chat_id: UUID,
        req: Request,
        data: HumanToAgentRequest,
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
        
        chat_state = await self.__state_service.ensure_chat_state(
            db=db,
            chat_id=chat_resource.chat_id,
            input=data.input,
            user_id=user.user_id,
            agent_id=chat_resource.agent_id
        )

        self.__interactions_service.send_to_agent(state=chat_state)

        return CommonHttpResponse(
            detail="Request sent to agent"
        )

    def outgoing_interaction(
        self,
        chat_id: UUID,
        req: Request,
        data: AgentToHumanRequest,
        db: Session,
        background_tasks: BackgroundTasks
    ):
        chat_resource: Chat = self.__http_service.request_validation_service.verify_resource(
            service_key="chats_service",
            params={
                "db": db,
                "chat_id": chat_id
            },
            not_found_message="Chat not found"
        )

        incoming_message, outgoing_message = self.__messages_service.handle_messages(
            db=db, 
            chat_id=chat_id, 
            human_message=data.human_message, 
            ai_message=data.ai_message
        )

        background_tasks.add_task(
            self.__state_service.update_chat_state_history, 
            chat_resource.chat_id, 
            incoming_message, 
            outgoing_message, 
            16
        )

        return CommonHttpResponse(
            detail="Request received"
        )        

        