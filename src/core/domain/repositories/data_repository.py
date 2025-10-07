from abc  import ABC, abstractmethod
import uuid
from typing  import List, Optional, TypeVar, Generic

T = TypeVar('T')

class DataRepository(ABC, Generic[T]):
    @abstractmethod
    def create(self, data: T) -> T:
        raise NotImplementedError

    @abstractmethod
    def get_one(self, key: str, value: str | uuid.UUID) -> Optional[T]:
        raise NotImplementedError

    @abstractmethod
    def get_many(
        self,
        key: str, 
        value: str | uuid.UUID, 
        limit: int = None, 
        order_by=None, 
        desc: bool = False
    ) -> List[T]:
        raise NotImplementedError
    
    @abstractmethod
    def get_all(self,) -> List[T]:
        raise NotImplementedError

    @abstractmethod
    def update(self, key: str, value: str | uuid.UUID, changes: dict) -> Optional[T]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str, value: str | uuid.UUID) -> List[T] | T | None:
        raise NotImplementedError