from src.modules.chats.chats_models import Chat, ChatCreate, ChatUpdate
from src.core.repository.base_repository import BaseRepository
from typing import List
from sqlalchemy.orm import Session
from uuid import UUID
from src.core.decorators.service_error_handler import service_error_handler

class ChatsService():
    _MODULE = "chats.service"
    def __init__(self, repository: BaseRepository):
        self._repository: BaseRepository = repository

    @service_error_handler(module=_MODULE)
    def create(self, db: Session,  title: str, user_id: UUID) -> Chat:
        chat = Chat(
            title=title,
            user_id=user_id
        )
        return self._repository.create(db=db, data=chat)

    @service_error_handler(module=_MODULE)
    def resource(self, db: Session, chat_id: UUID) -> Chat | None:
        return self._repository.get_one(db=db, key="chat_id", value=chat_id)
        
    @service_error_handler(module=_MODULE)
    def collection(self, db: Session, user_id: UUID) -> List[Chat]:
        return self._repository.get_many(db=db, key="user_id", value=user_id)
    
    @service_error_handler(module=_MODULE)
    def update(self, db: Session, chat_id: UUID, changes: ChatUpdate) -> Chat:
        return self._repository.update(db=db, key="chat_id", value=chat_id, changes=changes.model_dump(exclude_unset=True))

    @service_error_handler(module=_MODULE)
    def delete(self, db: Session, chat_id: UUID)-> Chat:
        return self._repository.delete(db=db, key="chat_id", value=chat_id)