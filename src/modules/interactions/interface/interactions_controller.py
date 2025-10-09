import asyncio
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from uuid import UUID
import os
import httpx

from src.modules.state.domain.state_models import WorkerState

from src.modules.interactions.domain.interactions_models import HumanToAgentRequest
from src.modules.state.application.state_service import StateService
from src.modules.chats.application.messages_service import MessagesService
from src.modules.chats.domain.messages_models import MessagePublic
from src.modules.companies.domain.enitities import Company

from src.modules.users.domain.entities import User
from src.modules.chats.domain.entities import Chat

from src.core.utils.http.hmac import get_hmac_headers

from src.core.services.request_validation_service import RequestValidationService
from src.modules.agents.application.agents_service import AgentsService
from src.modules.chats.application.chats_service import ChatsService
from src.modules.interactions.application.use_cases.handle_interaction import HandleInteraction

class InteractionsController:
    def __init__(
        self, 
        handle_interaction: HandleInteraction
    ):
        self.__handle_interaction = handle_interaction

    async def incoming_interaction(
        self,
        chat_id: UUID,
        req: Request,
        data: HumanToAgentRequest
    )-> MessagePublic: 
        user: User = req.state.user
        company: Company = req.state.company

        message = await self.__handle_interaction.execute(
            agent_id=data.agent_id,
            chat_id=chat_id,
            input=data.input,
            company=company,
            user=user
        )

        return MessagePublic.model_validate(message, from_attributes=True)
    

   