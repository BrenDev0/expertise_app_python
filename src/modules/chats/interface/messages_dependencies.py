from fastapi import Depends

from src.modules.chats.domain.messages_repository import MessagesRepository
from src.modules.chats.application.messages_service import MessagesService
from src.modules.chats.interface.messages_controller import MessagesController


def get_messages_repository() -> MessagesRepository:
    return MessagesRepository()

def get_messages_service(
        repository: MessagesRepository = Depends(get_messages_repository)
) -> MessagesService:
    return MessagesService(
        repository=repository
    )

def get_messages_controller(
    service: MessagesService = Depends(get_messages_service)
) -> MessagesController:
    return MessagesController(
        messages_service=service
    )