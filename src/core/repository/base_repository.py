# app/repositories/base_repository.py
from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, List, Optional
from sqlalchemy import select, update, delete
import uuid

T = TypeVar("T") 

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def create(self, db: Session, data: T) -> T:
        db.add(data)
        db.commit()
        db.refresh(data)
        
        return data

    def get_one(self, db: Session, key: str, value: str | uuid.UUID) -> Optional[T]:
        stmt = select(self.model).where(getattr(self.model, key) == value)
        result = db.execute(stmt).scalar_one_or_none()
        
        return result

    def get_many(
        self, 
        db: Session, 
        key: str, 
        value: str | uuid.UUID, 
        limit: int = None, 
        order_by=None, 
        desc: bool = False
    ) -> List[T]:
        stmt = select(self.model).where(getattr(self.model, key) == value)
        if order_by:
            col = getattr(self.model, order_by)
            if desc:
                stmt = stmt.order_by(col.desc())
            else:
                stmt = stmt.order_by(col.asc())
        if limit is not None:
            stmt = stmt.limit(limit)
        return db.execute(stmt).scalars().all()
    
    def get_all(self, db: Session) -> List[T]:
        stmt = select(self.model)
        return db.execute(stmt).scalars().all()

    def update(self, db: Session,  key: str, value: str | uuid.UUID, changes: dict) -> Optional[T]:
        stmt = update(self.model).where(getattr(self.model, key) == value).values(**changes).returning(*self.model.__table__.c)
        result = db.execute(stmt)
        db.commit()
    
        updated_record = self.get_one(db=db, key=key, value=value)
        return updated_record

    def delete(self, db: Session, key: str, value: str | uuid.UUID) -> List[T] | T | None:
        stmt = delete(self.model).where(getattr(self.model, key) == value).returning(*self.model.__table__.c)
        result = db.execute(stmt)
        db.commit()
        
        deleted_rows = result.fetchall()  # Get all deleted rows
        
        if not deleted_rows:
            return None 
        
        if len(deleted_rows) == 1:
            return self.model(**deleted_rows[0]._mapping)
        else:
            return [self.model(**row._mapping) for row in deleted_rows]
    