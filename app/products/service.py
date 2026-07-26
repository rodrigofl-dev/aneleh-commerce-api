from sqlalchemy.orm import Session

from app.products.repository import ProductRepository
from app.categories.repository import CategoryRepository
from app.products.models import Product
from app.products.schemas import (
    ProductCreate,
    ProductStockUpdate,
    ProductUpdate,
)

from app.core.exceptions import (
    CategoryNotFoundError,
    ProductNotFoundError,
    StockCannotBeNegativeError,
)


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ProductRepository(db)
        self.category_repository = CategoryRepository(db)

    # API #

    def new_product(self, data: ProductCreate):
        self._404_if_not_category(data.category_id)

        product = Product(
            name=data.name,
            description=data.description,
            category_id=data.category_id,
            price=data.price,
        )

        return self.repository.save(product)

    def get_all(
        self,
        limit: int,
        offset: int,
        category_id: int | None,
        include_unavailable: bool,
    ) -> tuple[list[Product], int]:

        items = self.repository.get_all(
            limit=limit,
            offset=offset,
            category_id=category_id,
            include_unavailable=include_unavailable,
        )

        total = self.repository.count_all(
            category_id=category_id,
            include_unavailable=include_unavailable,
        )

        return items, total

    def get_by_id(self, id: int) -> Product:
        return self._get_or_404(id)

    def update(self, id: int, data: ProductUpdate) -> Product:
        product = self._get_or_404(id)

        if data.category_id:
            self._404_if_not_category(data.category_id)

        for field, value in data.model_dump(exclude_none=True).items():
            setattr(product, field, value)

        return self.repository.save(product)

    def delete(self, id: int) -> None:
        product = self._get_or_404(id)

        # Produto já está desativado
        if not product.active:
            return None

        product.active = False
        self.repository.save(product)

        return None

    def update_stock(self, id: int, data: ProductStockUpdate) -> Product:
        product = self._get_or_404(id)

        new_quantity = product.stock_quantity + data.quantity_change
        if new_quantity < 0:
            raise StockCannotBeNegativeError(
                details={
                    "stock_before": product.stock_quantity,
                    "stock_after": new_quantity,
                }
            )

        product.stock_quantity = new_quantity

        # TODO: registrar na tabela de auditoria

        return self.repository.save(product)

    # Helpers #

    def _404_if_not_category(self, id: int) -> None:
        if self.category_repository.get_by_id(id) is None:
            raise CategoryNotFoundError

    def _get_or_404(self, id: int) -> Product:
        product = self.repository.get_by_id(id)
        if not product:
            raise ProductNotFoundError

        return product
