"""Seeds initial demo data.

Run with: docker compose exec server python -m app.scripts.seed

Safe to run multiple times (idempotent) — checks for existing records
before inserting anything.
"""

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.users.models import User
from app.users.repository import UserRepository

# Demo credentials only — this file is committed to version control on
# purpose (see 07-deployment.md, section 5). Never reuse this password
# for anything beyond local development.
ADMIN_NAME = "Admin"
ADMIN_EMAIL = "admin@anelehcommerce.com"
ADMIN_PASSWORD = "p@ss123"


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


def main() -> None:
    db = SessionLocal()
    try:
        seed_admin_user(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
