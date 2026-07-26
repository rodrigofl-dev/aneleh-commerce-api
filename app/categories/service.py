from sqlalchemy.orm import Session

from app.categories.repository import CategoryRepository
from app.products.repository import ProductRepository
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
        self.products_repository = ProductRepository(db)

    # API #

    def get_all(self, limit: int, offset: int) -> tuple[list[Category], int]:
        items = self.repository.get_all(limit=limit, offset=offset)
        total = self.repository.count_all()

        return items, total

    def get_by_id(self, id: int) -> Category:
        return self._get_or_404(id)

    def new_category(self, data: CategoryCreate) -> Category:
        self._raise_if_duplicate(data.name)

        category = Category(
            name=data.name,
        )

        return self.repository.save(category)

    def update(self, id: int, data: CategoryUpdate) -> Category:
        category = self._get_or_404(id)

        if data.name and data.name != category.name:
            self._raise_if_duplicate(data.name)
            category.name = data.name

        return self.repository.save(category)

    def delete(self, id: int) -> None:
        category = self._get_or_404(id)

        if self.products_repository.count_by_category(category.id) > 0:
            raise CategoryHasProductsError

        self.repository.delete(category)

    # Helpers #

    def _get_or_404(self, id: int) -> Category:
        category = self.repository.get_by_id(id)
        if not category:
            raise CategoryNotFoundError

        return category

    def _raise_if_duplicate(self, name: str) -> None:
        if self.repository.get_by_name(name):
            raise CategoryAlreadyExistsError
