from fastapi import Depends

from src.modules.chats.application.chats_service import ChatsService
from src.modules.chats.interface.chats_controller import ChatsController
from src.core.domain.repositories.data_repository import DataRepository
from src.modules.chats.infrastructure.sqlalchemy_chats_repository import SqlAchemyChatsRepsitory


def get_chats_repository() -> DataRepository:
    return SqlAchemyChatsRepsitory()

def get_chats_service(
    repository: DataRepository = Depends(get_chats_repository)
) -> ChatsService:
    return ChatsService(
        repository=repository
    )

def get_chats_controller(
    service: ChatsService = Depends(get_chats_service)
) -> ChatsController:
    return ChatsController(
        chats_service=service
    )