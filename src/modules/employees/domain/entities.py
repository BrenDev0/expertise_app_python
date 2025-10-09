from pydantic import BaseModel
from  typing  import Optional
from uuid  import UUID

from src.modules.users.domain.entities import User

class Employee(BaseModel):
    employee_id: Optional[UUID] = None
    user_id: UUID
    company_id: UUID
    position: Optional[str] = None
    is_manager: bool = False
    user: Optional[User] =  None