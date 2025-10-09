from fastapi import Depends


from src.modules.interactions.interface.interactions_controller import InteractionsController
from src.modules.state.application.state_service import StateService
from  src.modules.chats.application.messages_service import MessagesService
from src.modules.chats.interface.messages_dependencies import get_messages_service
from src.modules.state.interface.state_dependencies import get_state_service


def get_interactions_controller(
    state_service: StateService = Depends(get_state_service),
    messages_service: MessagesService = Depends(get_messages_service)
) -> InteractionsController:
    return InteractionsController(
        state_service=state_service,
        messages_service=messages_service
    )

