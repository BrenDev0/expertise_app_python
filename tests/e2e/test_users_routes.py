from dotenv import load_dotenv
load_dotenv()


import os
import hmac
import hashlib
import time

import pytest
from fastapi.testclient import TestClient
from src.server import app






client = TestClient(app)

verification_token = os.getenv("TEST_VERIFICATION_TOKEN")
token = os.getenv("TEST_TOKEN")


verification_header = {
    "Authorization": f"Bearer {verification_token}"
}

auth_header = {
    "Authorization": f"Bearer {token}"
}



# def test_create_user_success():
#     with TestClient(app) as client:
#         payload = {
#             "name": "test user",
#             "email": "testemail_TEST@gmail.com",
#             "phone": "123456",
#             "password": "carpincha",
#             "code": 123456 
#         }

#         res = client.post(
#             "/users/verified/create",
#             headers=verification_header,
#             json=payload
#         )

#         assert res.status_code == 201
#         assert res.json()["detail"] == "User created"
#         assert "token" in res.json()


def test_create_user_missing_fields():
    with TestClient(app) as client:
        payload = {
                "name": "test user",
                "email": "testemail@gmail.com",
                "phone": "123456",
                "code": 123456 
            }

        res = client.post(
            "/users/verified/create",
            headers=verification_header,
            json=payload
        )

        assert res.status_code == 422

def test_create_user_invalid_verification_code():
    with TestClient(app) as client:
        payload = {
                "name": "test user",
                "email": "testemail@gmail.com",
                "phone": "123456",
                "password": "fhfhfhfh",
                "code": 123457
            }

        res = client.post(
            "/users/verified/create",
            headers=verification_header,
            json=payload
        )

        assert res.status_code == 403

def test_resource_request_success():
    with TestClient(app) as client:

        res = client.get(
            "/users/secure/resource",
            headers=auth_header
        )

        assert res.status_code == 200
        assert "name" in res.json()
        assert "email" in res.json()
        assert "phone" in  res.json()
        assert "createdAt" in res.json()
        assert "userId" in res.json()
        assert "isAdmin" in res.json()
        assert "password" not in res.json()




def test_login_success():
    with TestClient(app) as client:
        
        res = client.post(
            "/users/login",
           
            json={
                "email": "testemail_TEST@gmail.com",
                "password": "carpincha"
            }
        )

        print(res.json(), "RESPONSE")
        assert res.status_code == 200
        assert "token" in res.json()



def test_login_incorrect_password():
    with TestClient(app) as client:
        res = client.post(
            "/users/login",
            json={
                "email": "testemail@gmail.com",
                "password": "pass"
            }
        )

        assert res.status_code == 400
        assert res.json()["detail"] == "Incorrect email or password"


def test_update_user_profile_success():
    with TestClient(app) as client:
        payload = {
            "name": "Updated Name",
            "phone": "987654321"
        }
        res = client.patch(
            "/users/secure/update",
            headers=auth_header,
            json=payload
        )
        assert res.status_code == 200
        assert res.json()["detail"] == "User profile updated"

def test_update_user_password_requires_old_password():
    with TestClient(app) as client:
        payload = {
            "password": "newpassword123"
        }
        res = client.patch(
            "/users/secure/update",
            headers=auth_header,
            json=payload
        )
        assert res.status_code == 400
        assert res.json()["detail"] == "Previous password required to update password"

# def test_delete_user():
#     delete_token = ""

#     with TestClient(app) as client:
#         res = client.delete(
#             "/users/secure/delete",
#             headers={
#                 "Authorization": f"Bearer {delete_token}"
#             }
#         )

#         assert res.status_code == 200
#         assert res.json()["detail"] == "User deleted"



            