from fastapi import APIRouter, Depends, status, Query

from sqlalchemy.orm import Session
from app.core.deps import get_db, require_role
from app.categories.schemas import (
    CategoryOut,
    CategoryCreate,
    CategoryUpdate,
    CategoryListResponse,
)
from app.categories.service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(
    "",
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    service = CategoryService(db)
    return service.new_category(data)


@router.get("", response_model=CategoryListResponse)
def get_all(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    service = CategoryService(db)
    items, total = service.get_all(limit, offset)
    return CategoryListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{id}", response_model=CategoryOut)
def get_by_id(id: int, db: Session = Depends(get_db)):
    service = CategoryService(db)
    return service.get_by_id(id)


@router.patch(
    "/{id}",
    response_model=CategoryOut,
    dependencies=[Depends(require_role("admin"))],
)
def update(id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    service = CategoryService(db)
    return service.update(id, data)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
def delete_category(id: int, db: Session = Depends(get_db)):
    service = CategoryService(db)
    return service.delete(id)
