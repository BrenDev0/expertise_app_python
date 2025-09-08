from fastapi import APIRouter, Body, Depends
from src.modules.interactions.interactions_controller import InteractionsController
from  src.modules.interactions.interactions_models import HumanToAgentRequest
from src.core.dependencies.container import Container
from sqlalchemy.orm import Session
from src.core.database.session import get_db_session
from src.modules.state.state_models import WorkerState
from src.core.middleware.hmac_verification import verify_hmac
from uuid import UUID

router = APIRouter(
    prefix="/interactions",
    tags=["Interactions"]
)

def get_controller() -> InteractionsController:
    controller = Container.resolve("interactions_controller")
    return controller


@router.post("/internal/incomming/{chat_id}", status_code=202, response_model=WorkerState)
async def internal_incomming_interaction(
    chat_id: UUID,
    data: HumanToAgentRequest = Body(...),
    _: None = Depends(verify_hmac),
    db: Session = Depends(get_db_session),
    controller: InteractionsController = Depends(get_controller)
):
    """
    ## HMAC protected for internal use only
    """

    return await controller.incoming_interaction(
        chat_id=chat_id,
        data=data,
        db=db
    )
