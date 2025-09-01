import pytest
from unittest.mock import Mock
import uuid

from src.modules.documents.documents_service import DocumentsService
from src.modules.documents.documents_models import Document
from src.modules.companies.companies_models import Company 

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def mock_data_handler():
    mock_handler = Mock()
    mock_handler.encryption_service.encrypt.return_value = "encrypted_url"
    return mock_handler

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def documents_service(mock_repository, mock_data_handler):
    return DocumentsService(respository=mock_repository, data_hander=mock_data_handler)

def test_create_returns_document(mock_db, mock_repository, mock_data_handler, documents_service):
    company_id = uuid.uuid4()
    filename = "test_file.pdf"
    url = "https://example.com/file.pdf"
    mock_document = Mock(spec=Document)
    mock_repository.create.return_value = mock_document

    result = documents_service.create(db=mock_db, company_id=company_id, filename=filename, url=url)

    assert result == mock_document
    mock_data_handler.encryption_service.encrypt.assert_called_once_with(url)
    mock_repository.create.assert_called_once()
    # Check that create was called with a Document instance
    call_args = mock_repository.create.call_args
    assert call_args[1]['db'] == mock_db
    created_document = call_args[1]['data']
    assert created_document.company_id == company_id
    assert created_document.filename == filename
    assert created_document.url == "encrypted_url"

def test_collection_returns_documents_list(mock_db, mock_repository, mock_data_handler, documents_service):
    company_id = uuid.uuid4()
    mock_document1 = Mock(spec=Document)
    mock_document2 = Mock(spec=Document)
    mock_repository.get_many.return_value = [mock_document1, mock_document2]

    result = documents_service.collection(db=mock_db, company_id=company_id)

    assert result == [mock_document1, mock_document2]
    mock_repository.get_many.assert_called_once_with(
        db=mock_db,
        key="company_id",
        value=company_id
    )

def test_delete_returns_deleted_document(mock_db, mock_repository, mock_data_handler, documents_service):
    document_id = uuid.uuid4()
    mock_document = Mock(spec=Document)
    mock_repository.delete.return_value = mock_document

    result = documents_service.delete(db=mock_db, document_id=document_id)

    assert result == mock_document
    mock_repository.delete.assert_called_once_with(
        db=mock_db,
        key="document_id",
        value=document_id
    )