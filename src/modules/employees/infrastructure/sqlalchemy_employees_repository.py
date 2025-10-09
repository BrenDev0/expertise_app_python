from sqlalchemy import String, Column, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from typing import Optional

from src.core.infrastructure.repositories.data.sqlalchemy_data_repository import SqlAlchemyDataRepository, Base
from src.modules.employees.domain.entities import Employee
from src.modules.users.domain.entities import User
from src.modules.users.infrastructure.sqlalchemy_user_repository import SqlAlchemyUser

class SqlAlchemyEmployee(Base):
    __tablename__ = "employees"

    employee_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id =  Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="Cascade"), nullable=False)
    company_id =  Column(UUID(as_uuid=True), ForeignKey("companies.company_id", ondelete="Cascade"), nullable=False)
    position = Column(String, nullable=True)
    is_manager = Column(Boolean, nullable=False, default=False)
    
    __table_args__ = (
        UniqueConstraint("user_id", "company_id", name="uq_user_company"),
    )

    user = relationship("SqlAlchemyUser")


class SqlAlchemyEmployeesRepository(SqlAlchemyDataRepository[Employee, SqlAlchemyEmployee]):
    def __init__(self):
        super().__init__(Employee)

    def _to_entity(self, model: SqlAlchemyEmployee) -> Employee:
        return Employee(
           employee_id=model.employee_id,
           user_id=model.user_id,
           company_id=model.company_id,
           position=model.position,
           is_manager=model.is_manager,
           user=self._user_to_entity(model.user) if model.user else None
        )
    
    def _user_to_entity(self, user_model: SqlAlchemyUser) -> Optional[User]:
        if not user_model:
            return None
        return User(
            user_id=user_model.user_id,
            name=user_model.name,
            phone=user_model.phone,
            email=user_model.email,
            email_hash=user_model.email_hash,
            password=user_model.password,
            is_admin=user_model.is_admin,
            created_at=user_model.created_at
        )
    
    def _to_model(self, entity: Employee) -> SqlAlchemyEmployee:
        data = entity.model_dump(exclude={'agent'})
        return SqlAlchemyEmployee(**data)
