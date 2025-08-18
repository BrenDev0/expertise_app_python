from fastapi import APIRouter, Depends, Request
from src.core.dependencies.container import Container
from src.modules.agents.agents_models import AgentPublic
from src.core.middleware.middleware_service import security
from src.core.middleware.auth_middleware import auth_middleware
from src.modules.agents.agents_controller import AgentsController
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from src.core.database.session import get_db_session

router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
    dependencies=[Depends(security)]
)

def get_controller() -> AgentsController:
    controller = Container.resolve("agents_controller")
    return controller

@router.post("/secure/resource/{agent_id}", status_code=200, response_model=AgentPublic)
def secure_create(
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