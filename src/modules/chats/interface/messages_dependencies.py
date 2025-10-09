from fastapi import Depends

from src.modules.chats.domain.messages_repository import MessagesRepository
from src.modules.chats.infrastructure.sqlalchemy_messages_repository import SqlAlchemyMessagesRepository
from src.modules.chats.application.messages_service import MessagesService
from src.modules.chats.interface.messages_controller import MessagesController
from src.modules.chats.application.chats_service import ChatsService
from src.modules.chats.interface.chats_dependencies import get_chats_service


def get_messages_repository() -> MessagesRepository:
    return SqlAlchemyMessagesRepository()

def get_messages_service(
        repository: MessagesRepository = Depends(get_messages_repository)
) -> MessagesService:
    return MessagesService(
        repository=repository
    )

def get_messages_controller(
    service: MessagesService = Depends(get_messages_service),
    chats_service: ChatsService = Depends(get_chats_service)
) -> MessagesController:
    return MessagesController(
        messages_service=service,
        chats_service=chats_service
    )