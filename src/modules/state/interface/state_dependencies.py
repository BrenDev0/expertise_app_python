from  fastapi import Depends

from src.core.domain.repositories.session_respository import SessionRepository
from src.core.infrastructure.repositories.session.redis_session_repository import RedisSessionRepository

from src.modules.chats.interface.messages_dependencies import get_messages_service
from src.modules.chats.application.messages_service import MessagesService
from src.modules.state.application.state_service import StateService



def get_session_repository() -> SessionRepository:
    return RedisSessionRepository()

def get_state_service(
    messages_service: MessagesService = Depends(get_messages_service),
    repository: SessionRepository = Depends(get_session_repository)
) -> StateService:
    return StateService(
        messages_service=messages_service,
        repository=repository
    )