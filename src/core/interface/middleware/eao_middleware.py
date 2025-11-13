import os
from fastapi import Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from  src.modules.agents.domain.models import AgentPublic

from src.core.interface.middleware.auth_middleware import auth_middleware
from src.modules.users.domain.entities import User

def eao_partition(
    req: Request,
  _: None = Depends(auth_middleware)
):
    user: User = req.state.user
    company_id = getattr(req.state, "company", None)
    eao_user_id = os.getenv("EAO_USER_ID")
    eao_companies = [company.strip() for company in os.getenv("EAO_COMPANIES", "").split(",") if company.strip()]

    eao_agent = AgentPublic(
        agent_id=os.getenv("EAO_AGENT_ID"),
        agent_name="Technician",
        agent_username="tech_assistant",
        description="Technician"
    )
    
    is_eao = False
    if company_id and company_id in eao_companies:
        is_eao = True
    elif str(user.user_id) == eao_user_id:
        is_eao = True

    if is_eao:
        req.state.eao_agent = eao_agent
    
    
    return None


def eao_restrictions(
    req: Request,
    _: None = Depends(auth_middleware)
):
    user: User = req.state.user
    company_id = getattr(req.state, "company", None)
    eao_user_id = os.getenv("EAO_USER_ID")
    eao_companies = [company.strip() for company in os.getenv("EAO_COMPANIES", "").split(",") if company.strip()]

    is_eao = False
    if company_id and company_id in eao_companies:
        is_eao = True
    elif str(user.user_id) == eao_user_id:
        is_eao = True

    if is_eao:
        raise HTTPException(status_code=403, detail="EAO clients do not have access to this route")


def eao_admin_restrictions(
    req: Request,
    _: None = Depends(auth_middleware)
):
    user: User = req.state.user
    eao_user_id = os.getenv("EAO_USER_ID")

    is_eao_admin = False
    if str(user.user_id) == eao_user_id:
        is_eao_admin = True

    if is_eao_admin:
        raise HTTPException(status_code=403, detail="EAO admin does not have access to this route")