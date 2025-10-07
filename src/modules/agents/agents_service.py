from src.core.repository.base_repository import BaseRepository
from  src.modules.agents.agents_models import Agent
from src.core.utils.decorators.service_error_handler import service_error_handler
from typing import List
from sqlalchemy.orm import Session
from uuid import UUID

class AgentsService:
    __MODULE = "agents.service"
    def __init__(self, respository: BaseRepository):
        self.__repository = respository

    @service_error_handler(module=f"{__MODULE}.resource")
    def resource(self, db: Session, agent_id: UUID) -> Agent | None:
        return self.__repository.get_one(
            db=db,
            key="agent_id",
            value=agent_id
        )
    
    @service_error_handler(f"{__MODULE}.read")
    def read(self, db: Session) -> List[Agent]:
        return self.__repository.get_all(db=db)