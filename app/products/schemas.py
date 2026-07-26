from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal

from app.core.schemas import PaginatedResponse


class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    category_id: int
    price: Decimal
    stock_quantity: int
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    category_id: int
    price: Decimal = Field(gt=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    description: str | None = Field(default=None, min_length=1)
    category_id: int | None = None
    price: Decimal | None = Field(default=None, gt=0)
    active: bool | None = None


class ProductStockUpdate(BaseModel):
    quantity_change: int
    reason: str = Field(min_length=1)


ProductListResponse = PaginatedResponse[ProductOut]
