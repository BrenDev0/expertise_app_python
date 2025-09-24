from src.modules.state.state_models import WorkerState
from src.core.models.http_responses import CommonHttpResponse
from src.core.services.http_service import HttpService
from src.modules.interactions.interactions_models import HumanToAgentRequest
from src.modules.state.state_service import StateService
from src.modules.chats.messages.messages_service import MessagesService
from src.modules.chats.messages.messages_models import MessagePublic
from sqlalchemy.orm import Session
from uuid import UUID
from src.modules.users.users_models import User
from src.modules.chats.chats_models import Chat
import asyncio
from fastapi import Request
from src.utils.http.hmac import get_hmac_headers
import os
import httpx

class InteractionsController:
    def __init__(
        self, 
        http_service: HttpService,
        state_service: StateService,
        messages_service: MessagesService
    ):
        self.__http_service = http_service
        self.__state_service = state_service
        self.__messages_service = messages_service

    async def incoming_interaction(
        self,
        chat_id: UUID,
        req: Request,
        data: HumanToAgentRequest,
        db: Session
    )-> MessagePublic: 
        user: User = req.state.user
        company_id = self.__http_service.request_validation_service.verify_company_in_request_state(req=req)

        chat_resource: Chat = self.__http_service.request_validation_service.verify_resource(
            service_key="chats_service",
            params={
                "db": db,
                "chat_id": chat_id
            },
            not_found_message="Chat not found"
        )

        self.__http_service.request_validation_service.validate_action_authorization(user.user_id, chat_resource.user_id)
        
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
            company_id=company_id
        )

        await self.__send_to_agent(state=worker_state)

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
                json=state
            )
            
            return response