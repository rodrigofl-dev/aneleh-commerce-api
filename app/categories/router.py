from fastapi import APIRouter, Depends, status, Query

from sqlalchemy.orm import Session
from app.core.deps import get_db, require_role
from app.categories.schemas import CategoryOut, CategoryCreate, CategoryUpdate
from app.core.schemas import PaginatedResponse
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


@router.get("", response_model=PaginatedResponse[CategoryOut])
def list_categories(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    service = CategoryService(db)
    items, total = service.get_all(limit, offset)
    return PaginatedResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{category_id}", response_model=CategoryOut)
def list_category(category_id: int, db: Session = Depends(get_db)):
    service = CategoryService(db)
    return service.get_by_id(category_id)


@router.patch(
    "/{category_id}",
    response_model=CategoryOut,
    dependencies=[Depends(require_role("admin"))],
)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    service = CategoryService(db)
    return service.update_category(category_id, data)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    service = CategoryService(db)
    return service.delete_category(category_id)
