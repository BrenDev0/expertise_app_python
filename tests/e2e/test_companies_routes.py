from dotenv import load_dotenv
load_dotenv()

import os

import pytest
from fastapi.testclient import TestClient
from src.server import app
from typing import List
import uuid

client = TestClient(app)

token = os.getenv("TEST_TOKEN")

auth_header = {
    "Authorization": f"Bearer {token}"
}

company_id = "218c9b2a-33d1-44c8-844a-5d302bc4a479"
# def test_create_company():
#     with TestClient(app) as client:
#         payload = {
#             "companyName": "test_company_delete",
#             "companyLocation": "nowhere",
#             "companySubscription": "gold"
#         }

#         res = client.post(
#             "/companies/secure/create",
#             headers=auth_header,
#             json=payload
#         )

#         assert res.status_code == 201
#         assert  res.json()["detail"] == "Company created"

def test_company_resource_success():
    with TestClient(app) as client:
        res = client.get(
            f"/companies/secure/resource/{company_id}",
            headers=auth_header
        )

        assert res.status_code == 200
        assert "companyId" in res.json()
        assert "userId" in res.json()
        assert "companyName" in res.json()
        assert "companyLocation" in res.json()
        assert "companySubscription" in res.json()
        assert "createdAt" in res.json()
        assert "s3Path" not in res.json()



def test_company_resource_not_found():
    with TestClient(app) as client:
        res = client.get(
            f"/companies/secure/resource/{uuid.uuid4()}",
            headers=auth_header
        )

        assert res.status_code == 404
        assert res.json()["detail"] == "Company not found"


def test_company_collection():
    with TestClient(app) as client:
        res = client.get(
            "/companies/secure/collection",
            headers=auth_header
        )

        assert res.status_code == 200
        assert isinstance(res.json(), List)



def test_company_update_success():
    with TestClient(app) as client:
        res = client.patch(
            f"/companies/secure/{company_id}",
            headers=auth_header,
            json={
                "companyName": "Updated name",
                "companySubscription": "free"
            }
        )
       
        assert res.status_code == 200
        assert res.json()["detail"] == "Company updated"

def test_company_update_not_found():
    with TestClient(app) as client:
        res = client.patch(
            f"/companies/secure/{uuid.uuid4()}",
            headers=auth_header,
            json={
                "companyName": "Updated name",
                "companySubscription": "free"
            }
        )

        assert res.status_code == 404
        assert res.json()["detail"] == "Company not found"

# def test_company_update_user_not_authorized():
#     with TestClient(app) as client:
#         other_user_token = ""
#         res = client.put(
#             f"/companies/secure/{company:_id}",
#             headers={
#                 "Authorization": f"Bearer {other_user_token}"
#             },
#             json={
#                 "companyName": "Updated name",
#                 "companySubscription": "free"
#             }
#         )

#         assert res.status_code == 403
#         assert res.json()["detail"] == "Forbidden"


def test_company_update_restricted_fields():
    with TestClient(app) as client:
        res = client.patch(
            f"/companies/secure/{company_id}",
            headers=auth_header,
            json={
                "s3Path": "Updated path",
                
            }
        )

        assert res.status_code == 422


# def test_delete_company_success():
#     with TestClient(app) as client:
#         res = client.delete(
#             f"/companies/secure/{company_id}",
#             headers=auth_header
#         )
      
#         assert res.status_code == 200
#         assert res.json()["detail"] == "Company deleted"


# def test_delete_company_unathorized():
#     other_user_token = ""
#     with TestClient(app) as client:
#         res = client.delete(
#             f"/companies/secure/{company_id}",
#             headers={
#                 "Authorization": f"Bearer {other_user_token}"
#             }
#         )

#         assert res.status_code == 403
#         assert res.json()["detail"] == "Forbidden"

def test_delete_company_not_found():
    with TestClient(app) as client:
        res = client.delete(
            f"/companies/secure/{uuid.uuid4()}",
            headers=auth_header
        )

        assert res.status_code == 404
        assert res.json()["detail"] == "Company not found"

def test_company_login_success():
    with TestClient(app) as client:
        res = client.get(
            f"/companies/secure/login/{company_id}",
            headers=auth_header
        )
        assert res.status_code == 200
        data = res.json()
        assert "detail" in data
        assert data["detail"] == "Login successful"
        assert "token" in data
        assert "companyId" in data
        assert isinstance(data["token"], str)