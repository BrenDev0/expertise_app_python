from pydantic import BaseModel
from uuid import UUID
from  typing import Optional

class Agent(BaseModel):
    agent_id: Optional[UUID] = None
    agent_name: str
    agent_username: str
    profile_pic: str
    endpoint: Optional[str] = None

class AgentAccess(BaseModel):
    agent_id: Optional[UUID] = None
    user_id: UUID
    agent: Optional[Agent] = None