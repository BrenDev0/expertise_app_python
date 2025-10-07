from abc import ABC, abstractmethod
from src.core.domain.repositories.data_repository import DataRepository
from typing import List, TypeVar
from uuid import UUID


T = TypeVar('T')

class UsersRepository(DataRepository[T]):
    @abstractmethod
    def bulk_delete(self, ids: List[UUID]) -> List[T] | None:
        raise NotImplementedError