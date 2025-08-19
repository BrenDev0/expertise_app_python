import pytest
from unittest.mock import Mock
import uuid

from src.modules.agents.agents_service import AgentsService
from src.modules.agents.agents_models import Agent

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def agents_service(mock_repository):
    return AgentsService(respository=mock_repository)

def test_resource_returns_agent(mock_db, mock_repository, agents_service):
    agent_id = uuid.uuid4()
    mock_agent = Mock(spec=Agent)
    mock_repository.get_one.return_value = mock_agent

    result = agents_service.resource(db=mock_db, agent_id=agent_id)

    assert result == mock_agent
    mock_repository.get_one.assert_called_once_with(
        db=mock_db,
        key="agent_id",
        value=agent_id
    )

def test_resource_returns_none(mock_db, mock_repository, agents_service):
    agent_id = uuid.uuid4()
    mock_repository.get_one.return_value = None

    result = agents_service.resource(db=mock_db, agent_id=agent_id)

    assert result is None
    mock_repository.get_one.assert_called_once_with(
        db=mock_db,
        key="agent_id",
        value=agent_id
    )

def test_read_returns_agents_list(mock_db, mock_repository, agents_service):
    mock_agent1 = Mock(spec=Agent)
    mock_agent2 = Mock(spec=Agent)
    mock_repository.get_all.return_value = [mock_agent1, mock_agent2]

    result = agents_service.read(db=mock_db)

    assert result == [mock_agent1, mock_agent2]
    mock_repository.get_all.assert_called_once_with(db=mock_db)