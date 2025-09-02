from fastapi import APIRouter, Request, BackgroundTasks, Body, Depends
from src.modules.interactions.interactions_controller import InteractionsController
from  src.modules.interactions.interactions_models import HumanToAgentRequest, AgentToHumanRequest
from src.core.dependencies.container import Container
from sqlalchemy.orm import Session
from  src.core.database.session import get_db_session
from src.core.middleware.auth_middleware import auth_middleware
from src.core.middleware.hmac_verification import verify_hmac
from src.core.models.http_responses import CommonHttpResponse
from uuid import UUID
from src.core.middleware.middleware_service import security

router = APIRouter(
    prefix="/interactions",
    tags=["Interactions"]
)

def get_controller() -> InteractionsController:
    controller = Container.resolve("interactions_controller")
    return controller


@router.post("/internal/incomming/{chat_id}", status_code=202, response_model=CommonHttpResponse, dependencies=[Depends(security)])
async def secure_send(
    chat_id: UUID,
    data: HumanToAgentRequest = Body(...),
    _: None = Depends(verify_hmac),
    db: Session = Depends(get_db_session),
    controller: InteractionsController = Depends(get_controller)
):
    return await controller.incoming_interaction(
        chat_id=chat_id,
        data=data,
        db=db
    )

@router.post("/internal/outgoing/{chat_id}", status_code=202, response_model=CommonHttpResponse)
def internal_receive(
    background_tasks: BackgroundTasks,
    chat_id: UUID,
    data: AgentToHumanRequest = Body(...),
    _: None = Depends(verify_hmac),
    db: Session = Depends(get_db_session),
    controller: InteractionsController = Depends(get_controller)
):
 
    return controller.outgoing_interaction(
        chat_id=chat_id,
        data=data,
        db=db,
        background_tasks=background_tasks
    )