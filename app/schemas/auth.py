from datetime import datetime

from pydantic import BaseModel


class LoginResponse(BaseModel):
    authorization_url: str
    state: str


class CallbackResponse(BaseModel):
    user_id: str
    character_id: int
    character_name: str
    linked: bool


class TokenRefreshResponse(BaseModel):
    character_id: str
    expires_at: datetime
