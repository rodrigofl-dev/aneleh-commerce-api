from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.users.schemas import UserOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut

    model_config = ConfigDict(from_attributes=True)
