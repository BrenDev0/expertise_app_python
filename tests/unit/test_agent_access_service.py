import pytest
from unittest.mock import Mock
import uuid

from src.modules.agents.agent_access.agent_access_service import AgentAccessService
from src.modules.agents.agent_access.agent_access_models import AgentAccess, AgentAccessCreate, AgentAccessDelete
from src.modules.agents.agents_models import Agent

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def service(mock_repository):
    return AgentAccessService(repository=mock_repository)

def test_create_many_creates_all(mock_db, mock_repository, service):
    user_id = uuid.uuid4()
    agent_ids = [uuid.uuid4(), uuid.uuid4()]
    data = AgentAccessCreate(agent_ids=agent_ids)
    created_objs = [Mock(spec=AgentAccess), Mock(spec=AgentAccess)]
    mock_repository.create_many.return_value = created_objs  # <-- fix here

    result = service.create_many(db=mock_db, data=data, user_id=user_id)

    assert result == created_objs
    mock_repository.create_many.assert_called_once_with(db=mock_db, user_id=user_id, agent_ids=agent_ids)

def test_collection_returns_agents(mock_db, mock_repository, service):
    user_id = uuid.uuid4()
    agents = [Mock(spec=Agent), Mock(spec=Agent)]
    mock_repository.get_agents_by_user.return_value = agents

    result = service.collection(db=mock_db, user_id=user_id)

    assert result == agents
    mock_repository.get_agents_by_user.assert_called_once_with(db=mock_db, user_id=user_id)

def test_remove_many_calls_repository(mock_db, mock_repository, service):
    user_id = uuid.uuid4()
    agent_ids = [uuid.uuid4(), uuid.uuid4()]
    data = AgentAccessDelete(agent_ids=agent_ids)

    service.remove_many(db=mock_db, data=data, user_id=user_id)

    mock_repository.delete_by_user_and_agents.assert_called_once_with(
        db=mock_db, user_id=user_id, agent_ids=agent_ids
    )