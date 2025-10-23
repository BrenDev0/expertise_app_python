from fastapi.encoders import jsonable_encoder
from uuid import UUID
import os
import httpx

from src.modules.state.domain.state_models import WorkerState
from src.modules.state.application.state_service import StateService
from src.modules.chats.application.messages_service import MessagesService
from src.modules.companies.domain.enitities import Company
from src.modules.users.domain.entities import User
from src.modules.chats.domain.entities import Message
from src.modules.agents.application.agents_service import AgentsService
from src.modules.chats.application.chats_service import ChatsService

from src.core.utils.http.hmac import get_hmac_headers

from src.core.interface.request_validation_service import RequestValidationService


class HandleInteraction:
    def __init__(
        self,
        agents_service: AgentsService,
        chats_service: ChatsService,
        messages_service: MessagesService,
        state_service: StateService
    ):
        self.__agents_service = agents_service
        self.__chats_service = chats_service
        self.__messages_service = messages_service
        self.__state_service = state_service

    async def execute(
        self,
        agent_id: UUID,
        chat_id: UUID,
        input: str,
        company: Company,
        user: User
    ) -> Message:
        agent_resource = self.__agents_service.resource(
            key="agent_id",
            value=agent_id
        )

        RequestValidationService.verify_resource(
            result=agent_resource,
            not_found_message="Agent not found"
        )

        chat_resource = self.__chats_service.resource(
            key="chat_id",
            value=chat_id
        )

        RequestValidationService.verify_resource(
            result=chat_resource,
            not_found_message="Chat not found"
        )

        RequestValidationService.verifiy_ownership(user.user_id, chat_resource.user_id)
        
        message = self.__messages_service.create(
            chat_id=chat_resource.chat_id,
            sender_id=user.user_id,
            message_type="human",
            text=input
        )

        worker_state: WorkerState = self.__state_service.ensure_chat_state(
            chat_id=str(chat_resource.chat_id),
            input=input,
            user_id=user.user_id,
            company_id=company.company_id
        )

        await self.__send_to_agent(
            state=worker_state,
            agent_id=agent_id
        )

        return message
    
    async def __send_to_agent(
        self,
        state: WorkerState,
        agent_id: UUID
    ):
        hmac_headers = get_hmac_headers(os.getenv("HMAC_SECRET"))
        agent_host = os.getenv("AGENTS_HOST")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://{agent_id}{agent_host}/interactions/internal/interact",
                headers=hmac_headers,
                json=jsonable_encoder(state)
            )
            
            return response