from pydantic import BaseModel

class CommonHttpResponse(BaseModel):
    detail: str

class ResponseWithToken(CommonHttpResponse):
    token: str