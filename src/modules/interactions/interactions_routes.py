from fastapi import APIRouter, Body, Depends, Request
from src.modules.interactions.interactions_controller import InteractionsController
from  src.modules.interactions.interactions_models import HumanToAgentRequest
from src.core.dependencies.container import Container
from sqlalchemy.orm import Session
from src.core.database.session import get_db_session
from src.modules.chats.messages.messages_models import MessagePublic
from src.core.middleware.auth_middleware import auth_middleware
from src.core.middleware.permissions import token_is_company_stamped
from src.core.middleware.middleware_service import security
from uuid import UUID

router = APIRouter(
    prefix="/interactions",
    tags=["Interactions"],
    dependencies=[Depends(security)]
)

def get_controller() -> InteractionsController:
    controller = Container.resolve("interactions_controller")
    return controller


@router.post("/secure/incomming/{chat_id}", status_code=200, response_model=MessagePublic)
async def internal_incomming_interaction(
    chat_id: UUID,
    req: Request,
    data: HumanToAgentRequest = Body(...),
    _: None = Depends(token_is_company_stamped), # handles auth
    db: Session = Depends(get_db_session),
    controller: InteractionsController = Depends(get_controller)
):
    """
    ## HMAC protected for internal use only
    """

    return await controller.incoming_interaction(
        chat_id=chat_id,
        req=req,
        data=data,
        db=db
    )
