from fastapi import Depends

from src.core.domain.repositories.data_repository import DataRepository
from src.core.infrastructure.repositories.data.sqlalchemy.sqlalchemy_data_repository import SqlAlchemyDataRepository

from src.modules.companies.companies_controller import CompaniesController
from src.modules.companies.application.companies_service import CompaniesService
from src.modules.companies.domain.enitities import Company


def get_companies_repository() -> DataRepository:
    return SqlAlchemyDataRepository(Company)

def get_companies_service(
    repository: DataRepository = Depends(get_companies_repository)
) -> CompaniesService:
    return CompaniesService(
        respository=repository
    )

def get_companies_controller(
    companies_service: CompaniesService = Depends(get_companies_service)
) -> CompaniesController:
    return CompaniesController(
        companies_service=companies_service
    )