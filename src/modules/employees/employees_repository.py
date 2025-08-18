from src.core.repository.base_repository import BaseRepository
from src.modules.employees.employees_models import Employee
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID

class EmployeesRepository(BaseRepository):
    def __init__(self):
        super().__init__(Employee)

    def get_by_user_and_company(self, db: Session, user_id: UUID, company_id: UUID) -> Employee | None :
        stmt = select(self.model).where(
            (self.model.company_id == company_id ) &
            (self.model.user_id == user_id)
        )
        return db.execute(stmt).scalar_one_or_none()
