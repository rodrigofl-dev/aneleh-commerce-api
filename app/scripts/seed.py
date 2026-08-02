"""Seeds initial demo data.

Run with: docker compose exec server python -m app.scripts.seed

Safe to run multiple times (idempotent) — checks for existing records
before inserting anything.
"""

import random
from decimal import Decimal

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.users.models import User
from app.users.repository import UserRepository
from app.categories.models import Category
from app.categories.repository import CategoryRepository
from app.products.models import Product
from app.products.repository import ProductRepository
from app.products.service import ProductService
from app.products.schemas import ProductStockUpdate

# Demo credentials only — this file is committed to version control on
# purpose (see 07-deployment.md, section 5). Never reuse this password
# for anything beyond local development.
ADMIN_NAME = "Admin"
ADMIN_EMAIL = "admin@anelehcommerce.com"
ADMIN_PASSWORD = "123"

# Nomes curados de propósito, em vez de gerados (ex: Faker) — o objetivo do
# NFR-09 é alguém abrir o Swagger e reconhecer um catálogo de e-commerce de
# verdade, não texto genérico tipo lorem ipsum.
CATALOG: dict[str, list[str]] = {
    "Eletrônicos": [
        "Smartphone X200",
        "Notebook Ultra 14",
        "Fone Bluetooth Pro",
        "Smartwatch Fit 3",
        "Câmera Digital 4K",
    ],
    "Livros": [
        "O Guia do Programador Pragmático",
        "Clean Code",
        "Python Fluente",
        "Arquitetura Limpa",
        "Refactoring",
    ],
    "Casa e Cozinha": [
        "Liquidificador Turbo",
        "Panela de Pressão 5L",
        "Cafeteira Elétrica",
        "Air Fryer 4L",
        "Jogo de Panelas Inox",
    ],
    "Esportes": [
        "Bola de Futebol Oficial",
        "Tênis de Corrida Runner",
        "Halteres 5kg (par)",
        "Bicicleta Aro 29",
        "Colchonete Yoga",
    ],
}

# Faixa de preço só pra variar o catálogo — não representa preço real de mercado.
PRICE_RANGE = (Decimal("19.90"), Decimal("2499.90"))


def seed_admin_user(db) -> None:
    repository = UserRepository(db)

    if repository.get_by_email(ADMIN_EMAIL) is not None:
        print(f"Admin user already exists ({ADMIN_EMAIL}). Skipping.")
        return

    admin_role = repository.get_role_by_name("admin")
    if admin_role is None:
        raise RuntimeError(
            "Role 'admin' not found. Run 'alembic upgrade head' before seeding."
        )

    admin = User(
        name=ADMIN_NAME,
        email=ADMIN_EMAIL,
        role_id=admin_role.id,
        password_hash=hash_password(ADMIN_PASSWORD),
    )
    repository.save(admin)
    print(f"Admin user created: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")


def _random_price() -> Decimal:
    low, high = PRICE_RANGE
    value = random.uniform(float(low), float(high))
    # Decimal(str(...)) evita erro de ponto flutuante binário
    # (Decimal(0.1) != Decimal("0.1")) — sempre construir a partir da string.
    return Decimal(str(round(value, 2)))


def _random_stock_amount() -> int:
    # Quantidade que será aplicada via PATCH /products/{id}/stock, nunca
    # atribuída direto ao criar o produto (POST /products sempre nasce
    # com stock_quantity=0 — ver 05-api-design.md, seção 5).
    return random.randint(5, 100)


def seed_categories_and_products(db) -> None:
    category_repository = CategoryRepository(db)
    product_repository = ProductRepository(db)
    product_service = ProductService(db)

    for category_name, product_names in CATALOG.items():
        category = category_repository.get_by_name(category_name)
        if category is None:
            category = category_repository.save(Category(name=category_name))
            print(f"Category created: {category_name}")
        else:
            print(f"Category already exists ({category_name}). Skipping creation.")

        for index, product_name in enumerate(product_names):
            if product_repository.get_by_name(product_name) is not None:
                print(f"  Product already exists ({product_name}). Skipping.")
                continue

            product = Product(
                name=product_name,
                description=(
                    f"{product_name} — produto de demonstração "
                    f"da categoria {category_name}."
                ),
                category_id=category.id,
                price=_random_price(),
            )
            product = product_repository.save(product)

            # O primeiro produto de cada categoria fica com estoque zero de
            # propósito (07-deployment.md, seção 5: "produtos com estoque
            # zero e com estoque disponível, para demonstrar ambos os
            # casos"). Os demais recebem estoque via o mesmo endpoint de
            # ajuste que a aplicação usaria de verdade.
            if index != 0:
                product = product_service.update_stock(
                    product.id,
                    ProductStockUpdate(
                        quantity_change=_random_stock_amount(),
                        reason="Estoque inicial de demonstração (seed).",
                    ),
                )

            print(
                f"  Product created: {product_name} "
                f"(price={product.price}, stock={product.stock_quantity})"
            )


def main() -> None:
    db = SessionLocal()
    try:
        seed_admin_user(db)
        seed_categories_and_products(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
