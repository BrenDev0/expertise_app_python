from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Body

from src.modules.agents.domain.models import AgentPublic
from src.modules.agents.domain.models import AgentAccessCreate
from src.core.middleware.middleware_service import security
from src.core.middleware.auth_middleware import auth_middleware
from src.modules.agents.interface.agents_controller import AgentsController



from src.core.middleware.hmac_verification import verify_hmac
from src.core.middleware.permissions import is_manager
from src.core.middleware.permissions import token_is_company_stamped

from src.modules.employees.application.employees_service import EmployeesService
from src.modules.employees.interface.employees_dependencies import get_employees_service
from src.modules.agents.interface.agents_dependencies import get_agents_controller

router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
    dependencies=[Depends(security), Depends(verify_hmac)]
)

@router.put("/secure/access/{employee_id}", status_code=201, response_model=List[AgentPublic])
def secure_upsert_access(
    employee_id: UUID,
    req: Request,
    data: AgentAccessCreate = Body(...),
    _: None = Depends(is_manager),
    company: None = Depends(token_is_company_stamped),
    employees_service: EmployeesService = Depends(get_employees_service),
    controller: AgentsController = Depends(get_agents_controller)
):
    """
    ## Add agent access to employee

    This endpoint will grant agent access to the employee id.
    Only admin level users, and manager level employees have access to this endpoint. 
    """
    return controller.add_access(
        employee_id=employee_id,
        req=req,
        data=data,
        employees_service=employees_service
    )

@router.get("/secure/resource/{agent_id}", status_code=200, response_model=AgentPublic)
def secure_resource(
    agent_id: UUID,
    req: Request,
    _: None = Depends(auth_middleware),
    controller: AgentsController = Depends(get_agents_controller)
):
    """
    # Resource request

    This endpoint gets and agent by id.
    """
    return controller.resource_request(
        agent_id=agent_id,
        req=req
    )

@router.get("/secure/access/collection/{employee_id}", status_code=200, response_model=List[AgentPublic])
def acess_collection(
    employee_id: UUID,
    req: Request,
    _: None = Depends(is_manager),
    company = Depends(token_is_company_stamped),
    employees_service: EmployeesService = Depends(get_employees_service),
    controller: AgentsController = Depends(get_agents_controller)
):
    """
    ## Collection request

    This endpoint returns all agents the employee id has access to.
    """  
    return controller.agent_acccess_collection_request(
        employee_id=employee_id,
        req=req,
        employees_service=employees_service
    )


@router.get("/secure/collection", status_code=200, response_model=List[AgentPublic])
def secure_collection(
    req: Request,
    _: None = Depends(auth_middleware),
    employees_service: EmployeesService = Depends(get_employees_service),
    controller: AgentsController = Depends(get_agents_controller)
):
    """
    ## Collection request

    This endpoint returns all agents the current user has access to.
    """
    return controller.collection_request(
        req=req,
        employees_service=employees_service
    )

@router.get("/secure/read", status_code=200, response_model=List[AgentPublic])
def secure_read(
    req: Request,
    _: None = Depends(auth_middleware),
    controller: AgentsController = Depends(get_agents_controller)
):
    """
    ## Read REquest 

    This endpoint gets all agents in database.
    """

    return controller.read_request()
