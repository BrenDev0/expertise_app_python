from dotenv import load_dotenv
load_dotenv()
import os
import pytest
from src.core.dependencies.configure_container import configure_container
from src.core.dependencies.container import Container
from src.modules.documents.document_manager import DocumentManager


def test_delete_company_data():
    configure_container()
    document_manager: DocumentManager = Container.resolve("doument_manger")

    user_id = os.getenv("TEST_USER_ID")
    company_id = os.getenv("TEST_COMPANY_ID")

    result = document_manager.company_level_deletion(
        company_id=company_id,
        user_id=user_id
    )

    assert result == "Company documents deleted"
