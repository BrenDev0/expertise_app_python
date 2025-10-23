from pydantic import BaseModel, ConfigDict
from typing import Optional
from pydantic.alias_generators import to_camel
import uuid
from  datetime import datetime



class DocumentConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        str_min_length=1,
        serialize_by_alias=True,
        alias_generator=to_camel,
        extra='forbid'
    )

class DocumentPublic(DocumentConfig):
    document_id: uuid.UUID
    company_id: uuid.UUID
    filename: str
    file_type: str
    url: str
    uploaded_at: datetime
