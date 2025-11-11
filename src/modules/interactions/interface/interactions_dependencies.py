from fastapi import Depends

from src.modules.interactions.interface.interactions_controller import InteractionsController
from src.modules.state.application.state_service import StateService
from  src.modules.chats.application.messages_service import MessagesService
from src.modules.chats.interface.messages_dependencies import get_messages_service
from src.modules.state.interface.state_dependencies import get_state_service
from src.modules.interactions.application.use_cases.handle_interaction import HandleInteraction 
from src.modules.agents.application.agents_service import AgentsService
from src.modules.agents.interface.agents_dependencies import get_agents_service
from src.modules.chats.application.chats_service import ChatsService
from src.modules.chats.interface.chats_dependencies import get_chats_service


def get_handle_interaction_use_case(
    agents_service: AgentsService = Depends(get_agents_service),
    chats_service: ChatsService = Depends(get_chats_service),
    messages_service: MessagesService = Depends(get_messages_service),
    state_service: StateService = Depends(get_state_service)
) -> HandleInteraction:
    return HandleInteraction(
        agents_service=agents_service,
        chats_service=chats_service,
        messages_service=messages_service,
        state_service=state_service
    )

def get_interactions_controller(
    handle_interaction: HandleInteraction = Depends(get_handle_interaction_use_case)
) -> InteractionsController:
    return InteractionsController(
        handle_interaction=handle_interaction
    )

