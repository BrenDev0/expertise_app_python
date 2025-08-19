import pytest
from unittest.mock import Mock
import uuid

from src.modules.agents.employee_agents.employee_agents_service import EmployeeAgentService
from src.modules.agents.employee_agents.employee_agent_models import EmployeeAgent, EmployeeAgentCreate, EmployeeAgentDelete
from src.modules.agents.agents_models import Agent

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def service(mock_repository):
    return EmployeeAgentService(repository=mock_repository)

def test_create_many_creates_all(mock_db, mock_repository, service):
    employee_id = uuid.uuid4()
    agent_ids = [uuid.uuid4(), uuid.uuid4()]
    data = EmployeeAgentCreate(agent_ids=agent_ids)
    created_objs = [Mock(spec=EmployeeAgent), Mock(spec=EmployeeAgent)]
    mock_repository.create.side_effect = created_objs

    result = service.create_many(db=mock_db, data=data, employee_id=employee_id)

    assert result == created_objs
    assert mock_repository.create.call_count == len(agent_ids)
    for idx, agent_id in enumerate(agent_ids):
        call_args = mock_repository.create.call_args_list[idx][1]
        assert call_args["db"] == mock_db
        assert call_args["data"].agent_id == agent_id
        assert call_args["data"].employee_id == employee_id

def test_collection_returns_agents(mock_db, mock_repository, service):
    employee_id = uuid.uuid4()
    agents = [Mock(spec=Agent), Mock(spec=Agent)]
    mock_repository.get_agents_by_employee.return_value = agents

    result = service.collection(db=mock_db, employee_id=employee_id)

    assert result == agents
    mock_repository.get_agents_by_employee.assert_called_once_with(db=mock_db, employee_id=employee_id)

def test_remove_many_calls_repository(mock_db, mock_repository, service):
    employee_id = uuid.uuid4()
    agent_ids = [uuid.uuid4(), uuid.uuid4()]
    data = EmployeeAgentDelete(agent_ids=agent_ids)

    service.remove_many(db=mock_db, data=data, employee_id=employee_id)

    mock_repository.delete_by_employee_and_agents.assert_called_once_with(
        mock_db, employee_id, agent_ids
    )