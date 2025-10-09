from uuid import UUID
from abc import abstractmethod
from typing import List

from src.core.domain.repositories.data_repository import DataRepository
from src.modules.chats.domain.entities import Message

class MessagesRepository(DataRepository[Message]):
    @abstractmethod
    def search_by_content(
        self,
        content: str, 
        user_id: UUID
    ) -> List[Message]:
        raise NotImplementedError
        

