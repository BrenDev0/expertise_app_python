import os
from dotenv import load_dotenv
load_dotenv()

from abc import abstractmethod
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, create_engine
from sqlalchemy.orm import sessionmaker
from typing import TypeVar, Generic, Type, List, Optional, Generator
import uuid

from src.core.domain.repositories.data_repository import DataRepository

DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(DB_URL, pool_pre_ping=True)  
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Two type variables: E = Entity, M = Model
E = TypeVar("E")  # Domain Entity
M = TypeVar("M")  # SQLAlchemy Model

class SqlAlchemyDataRepository(DataRepository[E], Generic[E, M]):
    def __init__(self, model: Type[M]):
        self.model = model

    @staticmethod
    def __get_db_session() -> Generator[Session, None, None]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
        
    @contextmanager
    def _get_session(self):
        """Context manager for database sessions"""
        db = next(self.__get_db_session())
        try:
            yield db
        finally:
            db.close()

    @abstractmethod
    def _to_entity(self, model: M) -> E:
        """Convert SQLAlchemy model to domain entity"""
        raise NotImplementedError
    
    @abstractmethod
    def _to_model(self, entity: E) -> M:
        """Convert domain entity to SQLAlchemy model"""
        raise NotImplementedError

    def create(self, data: E) -> E:
        with self._get_session() as db:
            # Convert entity to model
            model_instance = self._to_model(data)
            db.add(model_instance)
            db.commit()
            db.refresh(model_instance)
            
            # Convert back to entity
            return self._to_entity(model_instance)

    def get_one(self, key: str, value: str | uuid.UUID) -> Optional[E]:
        stmt = select(self.model).where(getattr(self.model, key) == value)

        with self._get_session() as db:
            result = db.execute(stmt).scalar_one_or_none()
            return self._to_entity(result) if result else None

    def get_many(
        self,
        key: str, 
        value: str | uuid.UUID, 
        limit: int = None, 
        order_by=None, 
        desc: bool = False
    ) -> List[E]:
        stmt = select(self.model).where(getattr(self.model, key) == value)
        if order_by:
            col = getattr(self.model, order_by)
            if desc:
                stmt = stmt.order_by(col.desc())
            else:
                stmt = stmt.order_by(col.asc())
        if limit is not None:
            stmt = stmt.limit(limit)
        
        with self._get_session() as db:
            results = db.execute(stmt).scalars().all()
            return [self._to_entity(result) for result in results]
    
    def get_all(self) -> List[E]:
        stmt = select(self.model)

        with self._get_session() as db:
            results = db.execute(stmt).scalars().all()
            return [self._to_entity(result) for result in results]

    def update(self, key: str, value: str | uuid.UUID, changes: dict) -> Optional[E]:
        stmt = update(self.model).where(getattr(self.model, key) == value).values(**changes).returning(*self.model.__table__.c)

        with self._get_session() as db:
            result = db.execute(stmt)
            db.commit()
            
            updated_rows = result.fetchall()
            
            if not updated_rows:
                return None
            
            # Create model instance and convert to entity
            updated_model = self.model(**updated_rows[0]._mapping)
            return self._to_entity(updated_model)

    def delete(self, key: str, value: str | uuid.UUID) -> List[E] | E | None:
        stmt = delete(self.model).where(getattr(self.model, key) == value).returning(*self.model.__table__.c)

        with self._get_session() as db:
            result = db.execute(stmt)
            db.commit()
            
            deleted_rows = result.fetchall()
            
            if not deleted_rows:
                return None 
            
            if len(deleted_rows) == 1:
                deleted_model = self.model(**deleted_rows[0]._mapping)
                return self._to_entity(deleted_model)
            else:
                deleted_models = [self.model(**row._mapping) for row in deleted_rows]
                return [self._to_entity(model) for model in deleted_models]