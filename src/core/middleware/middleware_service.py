import os
import jwt
from typing import Dict
from fastapi import Request, HTTPException
from src.core.services.webtoken_service import WebTokenService
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer



security = HTTPBearer()
class MiddlewareService:
    def __init__(self):
        self.TOKEN_KEY = os.getenv("TOKEN_KEY")

    def get_auth_bearer(self, request: Request, web_token_service: WebTokenService):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unautrhorized, Missing required auth headers")
        
        token = auth_header.split(" ")[1]

        try:
            payload = web_token_service.decode_token(token=token)

            return payload
        except jwt.ExpiredSignatureError:
            print("token expired")
            raise HTTPException(status_code=403, detail="Expired Token")
        
        except jwt.InvalidTokenError:
            print("token invalid")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))
        



    

        
