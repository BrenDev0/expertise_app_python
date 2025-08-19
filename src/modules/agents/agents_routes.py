from fastapi import APIRouter, Depends, Request, Body
from src.core.dependencies.container import Container
from src.modules.agents.agents_models import AgentPublic
from src.modules.agents.agent_access.agent_access_models import AgentAccessCreate, AgentAccessDelete
from src.core.middleware.middleware_service import security
from src.core.middleware.auth_middleware import auth_middleware
from src.modules.agents.agents_controller import AgentsController
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from src.core.database.session import get_db_session
from src.core.models.http_responses import CommonHttpResponse

router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
    dependencies=[Depends(security)]
)

def get_controller() -> AgentsController:
    controller = Container.resolve("agents_controller")
    return controller


@router.post("/secure/access/{employee_id}", status_code=201, response_model=CommonHttpResponse)
def secure_add_access(
    employee_id: UUID,
    req: Request,
    data: AgentAccessCreate = Body(...),
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: AgentsController = Depends(get_controller)
):
    """
    ## Add agent access to employee

    This endpoint will grant agent access to the employee id.
    Only admin level users, and manager level employees have access to this endpoint. 
    """
    return controller.add_access(
        employee_id=employee_id,
        data=data,
        req=req,
        db=db
    )

@router.get("/secure/resource/{agent_id}", status_code=200, response_model=AgentPublic)
def secure_resource(
    agent_id: UUID,
    req: Request,
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: AgentsController = Depends(get_controller)
):
    """
    # Resource request

    This endpoint gets and agent by id.
    """
    return controller.resource_request(
        agent_id=agent_id,
        req=req,
        db=db 
    )

@router.get("/secure/collection/{employee_id}", status_code=200, response_model=List[AgentPublic])
def secure_collection(
    employee_id: UUID,
    req: Request,
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: AgentsController = Depends(get_controller)
):
    """
    ## Collection request

    This endpoint returns all agents the employee id has access to.
    """
    return controller.collection_request(
        employee_id=employee_id,
        req=req,
        db=db
    )

@router.get("/secure/read", status_code=200, response_model=List[AgentPublic])
def secure_read(
    req: Request,
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: AgentsController = Depends(get_controller)
):
    """
    ## Read REquest 

    This endpoint gets all agents in database.
    """

    return controller.read_request(db=db)

@router.delete("/secure/access/{employee_id}", status_code=200, response_model=CommonHttpResponse)
def secure_remove_access(
    employee_id: UUID,
    req: Request,
    data: AgentAccessDelete = Body(...),
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: AgentsController = Depends(get_controller)
): 
    """
    ## Add agent access to employee

    This endpoint will remove agent access to the employee id.
    Only admin level users, and manager level employees have access to this endpoint. 
    """
    return controller.remove_access(
        employee_id=employee_id,
        data=data,
        req=req,
        db=db
    )