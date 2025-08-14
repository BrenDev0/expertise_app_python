import pytest
from unittest.mock import Mock, patch
import uuid

with patch("src.core.decorators.service_error_handler.service_error_handler", lambda *a, **kw: (lambda f: f)):

    from src.modules.employees.employees_repository import EmployeesRepository
    from src.modules.employees.employees_service import EmployeesService
    from src.modules.employees.employees_models import EmployeeCreate, EmployeeUpdate, Employee


@pytest.fixture
def mock_repository():
    return Mock(spec=EmployeesRepository)

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def employees_service(mock_repository):
    return EmployeesService(
        repository=mock_repository
    )

user_id = uuid.uuid4()
company_id = uuid.uuid4()
employee_id = uuid.uuid4()

def test_create(mock_repository, mock_db, employees_service):
    employee_data = EmployeeCreate(
        position="engineer"
    )

    mock_employee = Mock(spec=Employee)

    mock_repository.create.return_value = mock_employee

    result = employees_service.create(
        db=mock_db,
        data=employee_data,
        user_id=user_id,
        company_id=company_id
    )

    assert result == mock_employee
    mock_repository.create.assert_called_once()

    data_passed = mock_repository.create.call_args[1]["data"]

    assert data_passed.position == employee_data.position
    assert data_passed.user_id == user_id
    assert data_passed.company_id == company_id


def test_resource_by_user_and_company(mock_db, mock_repository, employees_service):
    mock_employee = Mock(spec=Employee)

    mock_repository.get_by_user_and_company.return_value = mock_employee

    result = employees_service.resource_by_user_and_company(
        db=mock_db,
        company_id=company_id,
        user_id=user_id
    )

    assert result == mock_employee
    mock_repository.get_by_user_and_company.assert_called_once()

    args_passed = mock_repository.get_by_user_and_company.call_args[1]

    assert args_passed["company_id"] == company_id
    assert args_passed["user_id"] == user_id


def  test_resource(mock_db, mock_repository, employees_service):
    mock_employee = Mock(spec=Employee)

    mock_repository.get_one.return_value = mock_employee

    result = employees_service.resource(
        db=mock_db,
        employee_id=employee_id
    )

    assert result == mock_employee
    mock_repository.get_one.assert_called_once()

    args_passed = mock_repository.get_one.call_args[1]
    assert args_passed["key"] == "employee_id"
    assert  args_passed["value"] == employee_id


def test_collection(mock_db, mock_repository, employees_service):
    mock_employee_1 = Mock(spec=Employee)
    mock_employee_2 = Mock(spec=Employee)
    mock_collection = [mock_employee_1, mock_employee_2]

    mock_repository.get_many.return_value = mock_collection

    result = employees_service.collection(
        db=mock_db,
        company_id=company_id
    )

    assert result == mock_collection
    mock_repository.get_many.assert_called_once()

    args_passed = mock_repository.get_many.call_args[1]
    assert args_passed["key"] == "company_id"
    assert args_passed["value"] == company_id




def test_update(mock_db, mock_repository, employees_service):
    changes = EmployeeUpdate(
        position="chef"
    )

    mock_employee = Mock(spec=Employee)
    mock_repository.update.return_value = mock_employee

    result = employees_service.update(
        db=mock_db,
        employee_id=employee_id,
        changes=changes
    )

    assert result == mock_employee
    mock_repository.update.assert_called_once()

    args_passed = mock_repository.update.call_args[1]

    assert args_passed["key"] == "employee_id"
    assert args_passed["value"] == employee_id
    assert args_passed["changes"]["position"] == changes.position

def test_delete(mock_db, mock_repository, employees_service):
    mock_employee = Mock(spec=Employee)

    mock_repository.delete.return_value = mock_employee

    result = employees_service.delete(
        db=mock_db,
        employee_id=employee_id
    )

    assert result == mock_employee
    mock_repository.delete.assert_called_once()

    args_passed = mock_repository.delete.call_args[1]
    assert args_passed["key"] == "employee_id"
    assert args_passed["value"] == employee_id
 