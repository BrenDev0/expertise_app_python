from src.core.dependencies.container import Container
from src.core.repository.base_repository import BaseRepository
from src.core.services.http_service import HttpService
from src.modules.companies.companies_controller import CompaniesController
from src.modules.companies.companies_service import CompaniesService
from src.modules.companies.companies_models import Company

def configure_companies_dependencies(http_service: HttpService):
    repository = BaseRepository(Company)
    service = CompaniesService(
        respository=repository
    )
    controller = CompaniesController(
        http_service=http_service,
        companies_service=service
    )

    Container.register("companies_service", service)
    Container.register("companies_controller", controller)