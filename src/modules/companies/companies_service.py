from src.core.repository.base_repository import BaseRepository
from src.core.decorators.service_error_handler import service_error_handler
from src.modules.companies.companies_models import Company, CompanyCreate, CompanyUpdate
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

class CompaniesService:
    __MODULE = "companies.service"
    def __init__(self, respository: BaseRepository):
        self.__repository = respository
    
    @service_error_handler(module=f"{__MODULE}.create")
    def create(self, db: Session, data: CompanyCreate, user_id: UUID) -> Company: 
        new_company = Company(
            **data.model_dump(by_alias=False),
            user_id=user_id
        )

        return self.__repository.create(db=db, data=new_company)
    
    @service_error_handler(module=f"{__MODULE}.resource")
    def resource(self, db: Session, company_id: UUID) -> Company | None:
        return self.__repository.get_one(db=db, key="company_id", value=company_id)
    

    @service_error_handler(module=f"{__MODULE}.collection")
    def collection(self, db: Session, user_id: UUID) -> List[Company]:
        return self.__repository.get_many(db=db, key="user_id", value=user_id)
    
    @service_error_handler(module=f"{__MODULE}.update")
    def update(self, db: Session, company_id: UUID, changes: CompanyUpdate) -> Company:
        return self.__repository.update(
            db=db,
            key="company_id",
            value=company_id,
            changes=changes.model_dump(by_alias=False, exclude_unset=True)
        )
    
    @service_error_handler(module=f"{__MODULE}.delete")
    def delete(self, db: Session, company_id: UUID) -> Company:
        return self.__repository.delete(db=db, key="company_id", value=company_id)