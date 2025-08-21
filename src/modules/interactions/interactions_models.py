from pydantic import BaseModel, ConfigDict
from  pydantic.alias_generators import to_camel
from uuid import UUID

class InteractionConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=to_camel
    )

class InteractionRequest(InteractionConfig):
    input: str
    chat_id: UUID