from abc import abstractmethod
from src.core.domain.repositories.data_repository import DataRepository
from typing import List
from uuid import UUID

from src.modules.users.domain.entities import User


class UsersRepository(DataRepository[User]):
    @abstractmethod
    def bulk_delete(self, ids: List[UUID]) -> List[User] | None:
        raise NotImplementedError