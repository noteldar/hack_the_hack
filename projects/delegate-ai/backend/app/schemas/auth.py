from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: Optional[int] = None


class OAuth2Response(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_info: dict