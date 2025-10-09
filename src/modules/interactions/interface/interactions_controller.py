from fastapi import Request
from uuid import UUID

from src.modules.interactions.domain.interactions_models import HumanToAgentRequest
from src.modules.chats.domain.messages_models import MessagePublic
from src.modules.companies.domain.enitities import Company

from src.modules.users.domain.entities import User

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
    

   