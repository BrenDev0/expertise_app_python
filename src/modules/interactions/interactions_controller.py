from src.modules.state.state_models import WorkerState
from src.core.models.http_responses import CommonHttpResponse
from src.core.services.http_service import HttpService
from src.modules.interactions.interactions_models import HumanToAgentRequest
from src.modules.state.state_service import StateService
from sqlalchemy.orm import Session
from uuid import UUID
from src.modules.users.users_models import User
from src.modules.chats.chats_models import Chat
import asyncio

class InteractionsController:
    def __init__(
        self, 
        http_service: HttpService,
        state_service: StateService
    ):
        self.__http_service = http_service
        self.__state_service = state_service

    async def incoming_interaction(
        self,
        chat_id: UUID,
        data: HumanToAgentRequest,
        db: Session
    )-> WorkerState: 
        chat_resource: Chat = self.__http_service.request_validation_service.verify_resource(
            service_key="chats_service",
            params={
                "db": db,
                "chat_id": chat_id
            },
            not_found_message="Chat not found"
        )

        self.__http_service.request_validation_service.validate_action_authorization(str(data.user_id), str(chat_resource.user_id))
        
        worker_state: WorkerState = await self.__state_service.ensure_chat_state(
            db=db,
            chat_id=str(chat_resource.chat_id),
            input=data.input,
            user_id=data.user_id,
            company_id=data.company_id,
            agents=[str(agent.agent_id) for agent in chat_resource.agents]
        )

        return worker_state