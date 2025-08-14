import pytest 
from src.core.database.session import get_db_session
from src.modules.employees.employees_repository import EmployeesRepository

@pytest.fixture
def repository():
    return EmployeesRepository()

@pytest.fixture
def session():
    return get_db_session()

def test_repo_method(repository, session):
    result = repository.get_by_user_and_company()