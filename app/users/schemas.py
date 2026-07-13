from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr

RoleName = Literal["admin","customer"]


class RoleOut(BaseModel):
    id: int
    name: RoleName

    model_config = ConfigDict(from_attributes=True)


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleOut
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class UserRoleUpdate(BaseModel):
    role: RoleName
