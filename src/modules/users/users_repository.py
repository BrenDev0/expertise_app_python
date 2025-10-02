from src.core.repository.base_repository import BaseRepository
from src.modules.users.users_models import User
from  uuid import UUID
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import delete

class UsersRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    
    def bulk_delete(self, db: Session, ids: List[UUID]) -> List[User] | None:
        stmt = delete(self.model).where(self.model.user_id.in_(ids)).returning(*self.model.__table__.c)

        result = db.execute(stmt)
        db.commit()

        deleted_rows = result.fetchall()

        if not deleted_rows:
            return None
        else:
            return [self.model(**row._mapping) for row in deleted_rows]
        
