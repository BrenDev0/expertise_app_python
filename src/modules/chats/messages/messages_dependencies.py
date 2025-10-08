from fastapi import Depends

from src.core.dependencies.container import Container
from src.core.services.http_service import HttpService

from src.modules.chats.messages.messages_repository import MessagesRepository
from src.modules.chats.messages.messages_service import MessagesService
from src.modules.chats.messages.messages_controller import MessagesController


def configure_messages_dependencies(http_service: HttpService):
    repository = MessagesRepository()
    service = MessagesService(repository=repository)
    controller = MessagesController(messages_service=service)
    Container.register("messages_service", service)
    Container.register("messages_controller", controller) 


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