from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import PaginatedResponse


class CategoryOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)


CategoryListResponse = PaginatedResponse[CategoryOut]
