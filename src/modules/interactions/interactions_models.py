from pydantic import BaseModel, ConfigDict
from  pydantic.alias_generators import to_camel

class InteractionConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=to_camel
    )

class HumanToAgentRequest(InteractionConfig):
    input: str

class AgentToHumanRequest(InteractionConfig):
    human_message: str
    ai_message: str