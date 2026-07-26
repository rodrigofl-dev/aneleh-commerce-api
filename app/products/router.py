from fastapi import APIRouter, Depends, status, Query

from sqlalchemy.orm import Session
from app.core.deps import get_db, require_role

from app.products.schemas import (
    ProductOut,
    ProductCreate,
    ProductUpdate,
    ProductStockUpdate,
    ProductListResponse,
)
from app.products.service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
def new_product(data: ProductCreate, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.new_product(data)


@router.get("", response_model=ProductListResponse)
def get_all(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    category_id: int | None = Query(default=None),
    include_unavailable: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    items, total = service.get_all(limit, offset, category_id, include_unavailable)
    return ProductListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{id}", response_model=ProductOut)
def get_by_id(id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_by_id(id)


@router.patch(
    "/{id}",
    response_model=ProductOut,
    dependencies=[Depends(require_role("admin"))],
)
def update(id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.update(id, data)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
def delete(id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.delete(id)


@router.patch(
    "/{id}/stock",
    response_model=ProductOut,
    dependencies=[Depends(require_role("admin"))],
)
def update_stock(id: int, data: ProductStockUpdate, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.update_stock(id, data)
