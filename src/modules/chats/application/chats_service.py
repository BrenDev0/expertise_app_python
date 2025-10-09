from typing import List
from uuid import UUID

from src.core.utils.decorators.service_error_handler import service_error_handler
from src.modules.chats.domain.chats_models import ChatUpdate

from src.modules.chats.domain.entities import Chat
from src.core.domain.repositories.data_repository import DataRepository


class ChatsService():
    _MODULE = "chats.service"
    def __init__(self, repository: DataRepository):
        self._repository = repository

    @service_error_handler(module=_MODULE)
    def create(self, title: str, user_id: UUID) -> Chat:
        chat = Chat(
            title=title,
            user_id=user_id
        )
        return self._repository.create(data=chat)

    @service_error_handler(module=_MODULE)
    def resource(self, key: str, value: UUID | str) -> Chat | None:
        return self._repository.get_one(key=key, value=value)
        
    @service_error_handler(module=_MODULE)
    def collection(self, user_id: UUID) -> List[Chat]:
        return self._repository.get_many(key="user_id", value=user_id)
    
    @service_error_handler(module=_MODULE)
    def update(self, chat_id: UUID, changes: ChatUpdate) -> Chat:
        return self._repository.update(key="chat_id", value=chat_id, changes=changes.model_dump(exclude_unset=True))

    @service_error_handler(module=_MODULE)
    def delete(self, chat_id: UUID)-> Chat | None:
        return self._repository.delete(key="chat_id", value=chat_id)