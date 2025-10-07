from sqlalchemy import Column, String, Boolean, DateTime, func, delete
from sqlalchemy.dialects.postgresql import UUID
from src.core.database.database_models import Base 
import uuid
from typing import List

from src.modules.users.domain.entities import User
from src.modules.users.domain.users_repository import UsersRepository
from src.core.infrastructure.repositories.data.sqlalchemy.sqlalchemy_data_repository import SqlAlchemyDataRepository

class SqlAlchemyUser(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    email_hash = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class SqlAlchemyUsersRepository(SqlAlchemyDataRepository[User, SqlAlchemyUser], UsersRepository):
    def __init__(self):
        super().__init__(SqlAlchemyUser)
    
    def _to_entity(self, model: SqlAlchemyUser) -> User:
        return User(
            user_id=model.user_id,
            name=model.name,
            phone=model.phone,
            email=model.email,
            email_hash=model.email_hash,
            password=model.password,
            is_admin=model.is_admin,
            created_at=model.created_at
        )
    
    def _to_model(self, entity: User) -> SqlAlchemyUser:
        data = entity.model_dump(exclude={'user_id', 'created_at'} if not entity.user_id else set())
        return SqlAlchemyUser(**data)
    def bulk_delete(self,ids: List[UUID]) -> List[User] | None:
        
        stmt = delete(self.model).where(self.model.user_id.in_(ids)).returning(*self.model.__table__.c)

        with self._get_session() as db:
            result = db.execute(stmt)
            db.commit()

            deleted_rows = result.fetchall()

            if not deleted_rows:
                return None
            else:
                return [self.model(**row._mapping) for row in deleted_rows]