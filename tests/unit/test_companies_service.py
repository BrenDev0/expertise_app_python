import pytest
from unittest.mock import Mock, patch
import uuid



from src.core.repository.base_repository import BaseRepository

from src.modules.companies.companies_service import CompaniesService
from src.modules.companies.companies_models import CompanyCreate, Company, CompanyUpdate

@pytest.fixture
def mock_repository():
    return Mock(spec=BaseRepository)

@pytest.fixture
def companies_service(mock_repository):
    return CompaniesService(
        respository=mock_repository
    )

@pytest.fixture
def mock_db():
    return Mock()


def test_create_company(mock_db, companies_service, mock_repository):
    company_data = CompanyCreate(
        company_name="test company",
        company_location="nowhere"
    )

    mock_company = Mock(spec=Company)
    user_id = uuid.uuid4()

    mock_repository.create.return_value = mock_company

    result = companies_service.create(
        db=mock_db,
        data=company_data,
        user_id=user_id
    )

    assert result == mock_company
    mock_repository.create.assert_called_once()

    created_company = mock_repository.create.call_args[1]['data']
    assert created_company.company_name == company_data.company_name 
    assert created_company.user_id  == user_id


def test_company_resource(mock_db, mock_repository, companies_service):
    mock_company = Company(
        company_id=uuid.uuid4(),
        company_name="test company",
        company_location="nowhere",
        company_subscription="free",
        created_at="datetime",
        s3_path="some-path"
    )

    mock_repository.get_one.return_value = mock_company
    company_id = uuid.uuid4()

    result = companies_service.resource(
        db=mock_db,
        company_id=company_id
    )

    assert result == mock_company
    mock_repository.get_one.assert_called_once()
    company_args = mock_repository.get_one.call_args[1]
    assert company_args["key"] == "company_id"
    assert company_args["value"] == company_id


def test_company_collection(mock_db, mock_repository, companies_service):
    mock_company_1 = Mock(spec=Company)
    mock_company_2 = Mock(spec=Company)
    mock_company_3 = Mock(spec=Company)
    
    mock_collection = [ mock_company_1, mock_company_2, mock_company_3 ]
    mock_repository.get_many.return_value = mock_collection
    user_id = uuid.uuid4()
    result = companies_service.collection(
        db=mock_db,
        user_id=user_id
    )

    mock_repository.get_many.assert_called_once()
    assert result == mock_collection

    company_args = mock_repository.get_many.call_args[1]
    assert company_args["key"] == "user_id"
    assert company_args["value"] == user_id

def test_company_update(mock_db, mock_repository, companies_service):
    changes = CompanyUpdate(
        company_name="new name",
        company_subscription="gold"
    )

    mock_company = Mock(spec=Company)

    mock_repository.update.return_value = mock_company
    company_id = uuid.uuid4() 

    result = companies_service.update(
        db=mock_db,
        company_id=company_id,
        changes=changes
    )

    mock_repository.update.assert_called_once()
    assert result == mock_company

    company_args = mock_repository.update.call_args[1]
    assert company_args["key"] == "company_id"
    assert company_args["value"] == company_id


def test_company_delete(mock_db, mock_repository, companies_service):
    mock_company = Mock(spec=Company)

    mock_repository.delete.return_value = mock_company

    company_id = uuid.uuid4()

    result = companies_service.delete(
        db=mock_db,
        company_id=company_id
    )

    assert result == mock_company

    company_args = mock_repository.delete.call_args[1]
    assert company_args["key"] == "company_id"
    assert company_args["value"] == company_id


