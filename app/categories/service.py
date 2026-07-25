from sqlalchemy.orm import Session

from app.categories.repository import CategoryRepository
from app.categories.models import Category
from app.categories.schemas import CategoryCreate, CategoryUpdate

from app.core.exceptions import (
    CategoryNotFoundError,
    CategoryAlreadyExistsError,
    CategoryHasProductsError,
)


class CategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = CategoryRepository(db)

    # API #

    def get_all(self, limit: int, offset: int) -> tuple[list[Category], int]:
        items = self.repository.get_all(limit=limit, offset=offset)
        total = self.repository.count_all()

        return items, total

    def get_by_id(self, category_id: int) -> Category:
        return self._get_or_404(category_id)

    def new_category(self, data: CategoryCreate) -> Category:
        self._raise_if_duplicate(data.name)

        category = Category(
            name=data.name,
        )

        return self.repository.save(category)

    def update_category(self, category_id: int, data: CategoryUpdate) -> Category:
        category = self._get_or_404(category_id)

        if data.name and data.name != category.name:
            self._raise_if_duplicate(data.name)
            category.name = data.name

        return self.repository.save(category)

    def delete_category(self, category_id: int) -> None:
        category = self._get_or_404(category_id)

        if self.repository.has_products(category.id):
            raise CategoryHasProductsError
    
        self.repository.delete(category)

    # Helpers #

    def _get_or_404(self, category_id: int) -> Category:
        category = self.repository.get_by_id(category_id)
        if not category:
            raise CategoryNotFoundError
        
        return category

    def _raise_if_duplicate(self, name: str) -> None:
        if self.repository.get_by_name(name):
            raise CategoryAlreadyExistsError
