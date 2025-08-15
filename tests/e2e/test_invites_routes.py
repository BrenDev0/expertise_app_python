import os
import uuid
import pytest
from fastapi.testclient import TestClient
from src.server import app

client = TestClient(app)

token = os.getenv("TEST_TOKEN")
auth_header = {
    "Authorization": f"Bearer {token}"
}

company_id = ""
invite_id = ""

# def test_create_invite_success():
#     with TestClient(app) as client:
#         payload = {
#             "name": "Test User",
#             "email": f"testuser_@example.com",
#             "phone": "1234567890",
#             "position": "manager"
#         }
#         res = client.post(
#             f"/invites/secure/{company_id}",
#             headers=auth_header,
#             json=payload
#         )
#         assert res.status_code == 201
#         assert res.json()["detail"].lower().startswith("invita")

def test_create_invite_email_in_use():
    pass

def test_invite_collection():
    with TestClient(app) as client:
        res = client.get(
            f"/invites/secure/collection/{company_id}",
            headers=auth_header
        )
        assert res.status_code == 200
        assert isinstance(res.json(), list)
        if res.json():
            invite = res.json()[0]
            assert "inviteId" in invite
            assert "name" in invite
            assert "email" in invite
            assert "phone" in invite
            assert "position" in invite
            assert "companyId" in invite

def test_invite_resource_success():
    with TestClient(app) as client:
        res = client.get(
            f"/invites/secure/resource/{invite_id}",
            headers=auth_header
        )
        assert res.status_code == 200
        if res.json():
            invite = res.json()
            assert "inviteId" in invite
            assert "name" in invite
            assert "email" in invite
            assert "phone" in invite
            assert "position" in invite
            assert "companyId" in invite

def test_invite_update_success():
    with TestClient(app) as client:
        payload = {
            "position": "updated position"
        }
        res = client.put(
            f"/invites/secure/{invite_id}",
            headers=auth_header,
            json=payload
        )
        assert res.status_code == 200
        assert res.json()["detail"] == "Invite updated"
    

def test_invite_update_not_found():
    res = client.put(
        f"/invites/secure/{uuid.uuid4()}",
        headers=auth_header,
        json={"position": "senior analyst"}
    )
    assert res.status_code == 404
    assert "Invite not found" in res.json()["detail"]

# def test_invite_delete_success():
#     invite_id_delete = ""
#     res = client.delete(
#         f"/invites/secure/{invite_id_delete}",
#         headers=auth_header
#     )
#     print(res.json())
#     assert res.status_code  == 200

def test_invite_delete_not_found():
    res = client.delete(
        f"/invites/secure/{uuid.uuid4()}",
        headers=auth_header
    )
    print(res.json())
    assert res.status_code  == 404
