from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from pydantic.alias_generators import to_camel
import uuid

class AgentConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        str_min_length=1,
        alias_generator=to_camel,
        extra="forbid"
    )

class AgentPublic(AgentConfig):
    agent_id: uuid.UUID
    agent_name: str
    agent_username: str
    profile_pic: Optional[str] = None
    description: Optional[str] = None
    greetings: Optional[List] = None


class AgentAccessConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=to_camel
    )

class AgentAccessCreate(AgentAccessConfig):
    agent_ids: List[uuid.UUID]

class AgentAccessDelete(AgentAccessCreate):
    pass