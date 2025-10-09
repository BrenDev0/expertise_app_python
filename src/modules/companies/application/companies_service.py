from uuid import UUID
from typing import List

from src.core.domain.repositories.data_repository import DataRepository
from src.core.utils.decorators.service_error_handler import service_error_handler

from src.modules.companies.application.use_cases.delete_employees_accounts import DeleteEmployeeAccounts
from src.modules.companies.application.use_cases.delete_company_documents import DeleteCompanyDocuments
from src.modules.companies.domain.companies_models import CompanyCreate, CompanyUpdate
from src.modules.companies.domain.enitities import Company


class CompaniesService:
    __MODULE = "companies.service"
    def __init__(
        self, 
        respository: DataRepository,
        delete_employee_accounts: DeleteEmployeeAccounts,
        delete_company_documents: DeleteCompanyDocuments
    ):
        self.__repository = respository
        self.__delete_company_documents = delete_company_documents
        self.__delete_employee_accounts = delete_employee_accounts
    
    @service_error_handler(module=__MODULE)
    def create(self, data: CompanyCreate, user_id: UUID) -> Company: 
        new_company = Company(
            **data.model_dump(by_alias=False),
            user_id=user_id
        )

        return self.__repository.create(data=new_company)
    
    @service_error_handler(module=__MODULE)
    def resource(self, key: str, value: UUID | str) -> Company | None:
        return self.__repository.get_one(key="company_id", value=value)
    

    @service_error_handler(module=__MODULE)
    def collection(self, user_id: UUID) -> List[Company]:
        return self.__repository.get_many(key="user_id", value=user_id)
    
    @service_error_handler(module=f"{__MODULE}.update")
    def update(self, company_id: UUID, changes: CompanyUpdate) -> Company:
        return self.__repository.update(
            key="company_id",
            value=company_id,
            changes=changes.model_dump(by_alias=False, exclude_unset=True)
        )
    
    @service_error_handler(module=__MODULE)
    def delete(self, company_id: UUID, user_id: UUID) -> Company:
        ## delete company documents from all cloud providers and db
        self.__delete_company_documents.execute(
            user=user_id,
            company_id=company_id
        )

        ## delete users accounts of the employees
        self.__delete_employee_accounts.execute(company_id=company_id)


        return self.__repository.delete(key="company_id", value=company_id)
    
