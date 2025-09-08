from src.modules.state.state_models import WorkerState
from src.core.models.http_responses import CommonHttpResponse
from src.core.services.http_service import HttpService
from src.modules.interactions.interactions_models import HumanToAgentRequest, AgentToHumanRequest
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
        messaging_service: MessagesService,
        state_service: StateService
    ):
        self.__http_service = http_service
        self.__messages_service = messaging_service
        self.__state_service = state_service

    async def incoming_interaction(
        self,
        chat_id: UUID,
        data: HumanToAgentRequest,
        db: Session
    )-> WorkerState: 
        print("IN CONTROLLER")
        chat_resource: Chat = self.__http_service.request_validation_service.verify_resource(
            service_key="chats_service",
            params={
                "db": db,
                "chat_id": chat_id
            },
            not_found_message="Chat not found"
        )

        print(data.user_id, ";;;;;;;;USER:::::", ":::::::::company", chat_resource.user_id)

        self.__http_service.request_validation_service.validate_action_authorization(str(data.user_id), str(chat_resource.user_id))
        
        worker_state: WorkerState = await self.__state_service.ensure_chat_state(
            db=db,
            chat_id=chat_resource.chat_id,
            input=data.input,
            user_id=data.user_id,
            company_id=data.company_id,
            agents=chat_resource.agents
        )

        return worker_state

    def outgoing_interaction(
        self,
        chat_id: UUID,
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

        incoming_message = self.__messages_service.create(db=db, sender_id=chat_resource.user_id, message_type="human", text=data.human_message)
        outgoing_message = self.__messages_service.create(db=db, chat_id=chat_id, sender_id=data.agent_id, message_type="ai", text=data.ai_message)

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

        