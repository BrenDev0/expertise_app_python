from pydantic import BaseModel
from typing import List, Dict, Any
from uuid import UUID

class WorkerState(BaseModel):
    input: str
    chat_id: UUID
    company_id: UUID
    chat_history: List[Dict[str, Any]]
    user_id: UUID
    voice: bool