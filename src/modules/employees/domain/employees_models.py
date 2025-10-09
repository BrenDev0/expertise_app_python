import uuid
from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic.alias_generators import to_camel
from typing import Optional


class EmployeeConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=to_camel,
        extra="forbid"
    )

class EmployeeUser(EmployeeConfig):
    user_id: str
    name: str
    email: EmailStr
    phone: str

class EmployeeCreate(EmployeeConfig):
    password: str

class EmployeePublic(EmployeeConfig):
    employee_id: uuid.UUID
    company_id: uuid.UUID
    position: Optional[str] = None
    is_manager: bool
    user: EmployeeUser

class EmployeeUpdate(EmployeeConfig):
    position: str 