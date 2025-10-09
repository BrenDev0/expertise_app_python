from src.modules.state.domain.state_models import WorkerState

from src.modules.interactions.domain.interactions_models import HumanToAgentRequest
from src.modules.state.application.state_service import StateService
from src.modules.chats.application.messages_service import MessagesService
from src.modules.chats.domain.messages_models import MessagePublic
from src.modules.companies.domain.enitities import Company
from sqlalchemy.orm import Session
from uuid import UUID
from src.modules.users.domain.entities import User
from src.modules.chats.domain.chats_models import Chat
import asyncio
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from src.utils.http.hmac import get_hmac_headers
import os
import httpx
from src.core.services.request_validation_service import RequestValidationService
from src.modules.agents.application.agents_service import AgentsService
from src.modules.chats.application.chats_service import ChatsService

class InteractionsController:
    def __init__(
        self,
        state_service: StateService,
        messages_service: MessagesService
    ):
        self.__state_service = state_service
        self.__messages_service = messages_service

    async def incoming_interaction(
        self,
        chat_id: UUID,
        req: Request,
        data: HumanToAgentRequest,
        agents_service: AgentsService,
        chats_service: ChatsService,
        db: Session
    )-> MessagePublic: 
        user: User = req.state.user
        company: Company = req.state.company

        agent_resource = agents_service.resource(
            db=db,
            key="agent_id",
            value=data.agent_id
        )

        RequestValidationService.verify_resource(
            result=agent_resource,
            not_found_message="Agent not found"
        )


        chat_resource = chats_service.resource(
            db=db,
            key="chat_id",
            value=chat_id
        )

        RequestValidationService.verify_resource(
            result=chat_resource,
            not_found_message="Chat not found"
        )

        RequestValidationService.verifiy_ownership(user.user_id, chat_resource.user_id)
        
        message = self.__messages_service.create(
            db=db,
            chat_id=chat_resource.chat_id,
            sender_id=user.user_id,
            message_type="human",
            text=data.input
        )

        worker_state: WorkerState = await self.__state_service.ensure_chat_state(
            db=db,
            chat_id=str(chat_resource.chat_id),
            input=data.input,
            user_id=user.user_id,
            company_id=company.company_id
        )

        await self.__send_to_agent(
            state=worker_state,
            agent_id=data.agent_id
        )

        return MessagePublic.model_validate(message, from_attributes=True)
    

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