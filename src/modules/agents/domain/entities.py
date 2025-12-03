from pydantic import BaseModel
from uuid import UUID
from  typing import Optional, List

class Agent(BaseModel):
    agent_id: Optional[UUID] = None
    agent_name: str
    agent_username: str
    description: Optional[str] = None
    profile_pic: Optional[str] = None
    greetings: Optional[List[str]] = None

class AgentAccess(BaseModel):
    agent_id: Optional[UUID] = None
    user_id: UUID
    agent: Optional[Agent] = None