from fastapi import Request
from uuid import UUID

from src.core.domain.models.http_responses import CommonHttpResponse, ResponseWithToken

from src.modules.users.domain.entities import User
from src.modules.companies.domain.companies_models import CompanyCreate, CompanyPublic, CompanyUpdate
from src.modules.companies.application.companies_service import CompaniesService
from src.modules.companies.domain.enitities import Company
from src.core.interface.request_validation_service import RequestValidationService
from src.core.services.webtoken_service import WebTokenService


class CompaniesController:
    def __init__(
        self, 
        companies_service: CompaniesService
    ):
        self.__companies_service = companies_service

    def create_request(
        self,
        req: Request,
        data: CompanyCreate
    ) -> CompanyPublic: 
        user: User = req.state.user

        new_company = self.__companies_service.create(data=data, user_id=user.user_id)

        return self.__to_public(new_company)
    
    def resource_request(
        self,
        req: Request
    ) -> CompanyPublic:
        user: User = req.state.user
        company: Company = req.state.company

        return self.__to_public(company)


    def collection_request(
        self,
        req: Request
    ):
        user: User = req.state.user

        data = self.__companies_service.collection(user_id=user.user_id)

        return [
            self.__to_public(company) for company in data
        ]
    

    def update_request(
        self,
        req: Request,
        data: CompanyUpdate
    ) -> CompanyPublic:
        user: User = req.state.user

        company_resource: Company = self.__companies_service.resource(
            key="company_id",
            value=data.company_id
        )
        RequestValidationService.verify_resource(
            result=company_resource,
            not_found_message="Company not found"
        )

        RequestValidationService.verifiy_ownership(user.user_id, company_resource.user_id)

        updated_company = self.__companies_service.update(company_id=company_resource.company_id, changes=data)

        return self.__to_public(updated_company)
    
    def delete_request(
        self,
        company_id: UUID,
        req: Request
    ) -> CommonHttpResponse:
        user: User = req.state.user
   
        company_resource: Company = self.__companies_service.resource(
            key="company_id",
            value=company_id
        )

        RequestValidationService.verify_resource(
            result=company_resource,
            not_found_message="Company not found"
        )

        RequestValidationService.verifiy_ownership(user.user_id, company_resource.user_id)

        ## delete company documents from all cloud providers, employees and company from db 
        self.__companies_service.delete(company_id=company_resource.company_id)
     
        return CommonHttpResponse(
            detail="Company deleted"
        )
    

    def login(
        self,
        company_id: UUID,
        req: Request,
        web_token_service: WebTokenService
    ) -> ResponseWithToken:
        user: User = req.state.user

        company_resource: Company = self.__companies_service.resource(
            key="company_id",
            value=company_id
        )


        RequestValidationService.verifiy_ownership(user.user_id, company_resource.user_id)

        token_payload = {
            "user_id": str(user.user_id),
            "company_id": str(company_resource.company_id)
        }

        token = web_token_service.generate_token(token_payload, "7d")

        return ResponseWithToken(
            detail="Login successful",
            token=token,
            company_id=str(company_resource.company_id)
        )


    @staticmethod
    def __to_public(data: Company) -> CompanyPublic:
        return CompanyPublic.model_validate(data, from_attributes=True)

        