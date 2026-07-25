from sqlalchemy.orm import Session

from app.categories.models import Category
from app.products.models import Product


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Category | None:
        return self.db.query(Category).filter(Category.id == id).first()

    def get_by_name(self, name: str) -> Category | None:
        return self.db.query(Category).filter(Category.name == name).first()

    def get_all(self, limit: int = 20, offset: int = 0) -> list[Category]:
        return self.db.query(Category).limit(limit).offset(offset).all()

    def count_all(self) -> int:
        return self.db.query(Category).count()

    def has_products(self, id: int) -> bool:
        products = self.db.query(Product).filter(Product.category_id == id).count()
        return True if products > 0 else False

    def save(self, category: Category) -> Category:
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category: Category) -> None:
        self.db.delete(category)
        self.db.commit()
