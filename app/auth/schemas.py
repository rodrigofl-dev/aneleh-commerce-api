from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.users.schemas import UserOut


class NormalizeEmailMixin:
    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v):
        return v.lower() if isinstance(v, str) else v


class LoginRequest(NormalizeEmailMixin, BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(NormalizeEmailMixin, BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut

    model_config = ConfigDict(from_attributes=True)
