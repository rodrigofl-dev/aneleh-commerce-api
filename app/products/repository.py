from sqlalchemy.orm import Session

from app.products.models import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Product | None:
        return self.db.query(Product).filter(Product.id == id).first()

    def get_by_name(self, name: str) -> Product | None:
        return self.db.query(Product).filter(Product.name == name).first()

    def get_all(
        self,
        limit: int,
        offset: int,
        category_id: int | None,
        include_unavailable: bool,
    ) -> list[Product]:

        query = self._filtered_query(category_id, include_unavailable)
        return query.limit(limit).offset(offset).all()

    def count_all(
        self,
        category_id: int | None,
        include_unavailable: bool,
    ) -> int:
        return self._filtered_query(category_id, include_unavailable).count()

    def count_by_category(self, id: int) -> int:
        return self.db.query(Product).filter(Product.category_id == id).count()

    def save(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def _filtered_query(self, category_id: int | None, include_unavailable: bool):
        query = self.db.query(Product)

        if category_id is not None:
            query = query.filter(Product.category_id == category_id)

        if not include_unavailable:
            query = query.filter(Product.active.is_(True), Product.stock_quantity > 0)

        return query
