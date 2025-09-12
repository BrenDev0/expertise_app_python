from dotenv import load_dotenv
load_dotenv()

import os

import pytest
from fastapi.testclient import TestClient
from src.server import app
from typing import List
import uuid

client = TestClient(app)

invite_token = os.getenv("TEST_INVITE_TOKEN")
token = os.getenv("TEST_TOKEN")


verification_header = {
    "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2ZXJpZmljYXRpb25fY29kZSI6IjlmYTliNDU4LTNjZjItNDVkNC1hNTJlLWNmNzUwZWRkZjYwZCIsImV4cCI6MTc4OTI0MzU5NX0.-1h4q-GaI4-gkZoACpMil2GyjPSb6enu122jD1eKWv8"
}

auth_header = {
    "Authorization": f"Bearer {token}"
}


def test_employee_create_success():
    with TestClient(app) as client:
        res = client.post(
            "/employees/verified/create",
            headers=verification_header,
            json={
                "password": "carpincha"
            }
        )

    assert res.status_code == 201
    assert "token" in res.json()

def test_resource_success():
    employee_id = ""
    with TestClient(app) as client:
        res = client.get(
            f"/employees/secure/resource/{employee_id}",
            headers=auth_header
        )

        assert res.status_code == 200
        assert "employeeId" in res.json()

def test_resource_not_found():
    with TestClient(app) as client:
        res = client.get(
            f"/employees/secure/resource/{uuid.uuid4()}",
            headers=auth_header
        )

        assert res.status_code == 404
        assert res.json()["detail"] == "Employee not found"


def test_collection_success():
    company_id=""
    with TestClient(app) as client:
        res = client.get(
            f"/employees/secure/collection/{company_id}",
            headers=auth_header
        )

        assert res.status_code == 200
        assert isinstance(res.json(), List)

def test_collection_not_found():
    with TestClient(app) as client:
        res = client.get(
            f"/employees/secure/collection/{uuid.uuid4()}",
            headers=auth_header
        )

        assert res.status_code == 404
        assert res.json()["detail"] == "Company not found"

# def test_update_success():
#     employee_update = ""
#     with TestClient(app) as client:
#         res = client.put(
#             f"/employees/secure/{employee_update}",
#             headers=auth_header,
#             json=({
#                 "position": "updated role"
#             })
#         )
       
#         assert res.status_code == 200
#         assert res.json()["detail"] == "Employee updated"

# def test_delete_success():
#     with TestClient(app) as client:
#         employee_delete = ""
#         res = client.delete(
#             f"/employees/secure/{employee_delete}",
#             headers=auth_header,
#         )
#         print(res.json(), "RES::::::::::::")
#         assert res.status_code == 200
#         assert res.json()["detail"] == "Employee deleted"