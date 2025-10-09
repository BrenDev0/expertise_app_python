from fastapi import APIRouter, Body, Depends, Request
from src.modules.interactions.interface.interactions_controller import InteractionsController
from  src.modules.interactions.domain.interactions_models import HumanToAgentRequest

from src.modules.interactions.interface.interactions_dependencies import get_interactions_controller
from src.modules.chats.domain.messages_models import MessagePublic

from src.core.middleware.permissions import token_is_company_stamped
from src.core.middleware.middleware_service import security
from uuid import UUID

router = APIRouter(
    prefix="/interactions",
    tags=["Interactions"],
    dependencies=[Depends(security)]
)



@router.post("/secure/incomming/{chat_id}", status_code=200, response_model=MessagePublic)
async def internal_incomming_interaction(
    chat_id: UUID,
    req: Request,
    data: HumanToAgentRequest = Body(...),
    _: None = Depends(token_is_company_stamped), # handles auth
    controller: InteractionsController = Depends(get_interactions_controller)
):
    """
    ## HMAC protected for internal use only
    """

    return await controller.incoming_interaction(
        chat_id=chat_id,
        req=req,
        data=data
    )
