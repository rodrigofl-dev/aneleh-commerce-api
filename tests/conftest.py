import pymysql
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.core.security import create_access_token
from app.core.database import Base
from app.core.deps import get_db
from app.core.redis_client import redis_client
from app.main import app
from app.users.models import Role, User  # noqa: F401 (registers models on Base.metadata)

TEST_DATABASE_URL = "mysql+pymysql://root:root@db:3306/aneleh_commerce_test"


def _ensure_test_database_exists() -> None:
    url = make_url(TEST_DATABASE_URL)
    connection = pymysql.connect(
        host=url.host,
        port=url.port or 3306,
        user=url.username,
        password=url.password,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{url.database}`")
        connection.commit()
    finally:
        connection.close()


@pytest.fixture(scope="session")
def engine():
    """Creates the test database and tables once per test session."""
    _ensure_test_database_exists()

    test_engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=test_engine)

    # Seed required reference data (roles), mirroring the Alembic migration.
    with test_engine.connect() as connection:
        connection.execute(
            insert(Role),
            [{"id": 1, "name": "admin"}, {"id": 2, "name": "customer"}],
        )
        connection.commit()

    yield test_engine

    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture()
def db_session(engine):
    """Each test runs inside a transaction that is rolled back afterwards."""
    connection = engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(bind=connection)
    session = TestingSessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """FastAPI TestClient wired to the per-test transactional session."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def _cleanup_redis_blacklist():
    """Prevents leftover test tokens from accumulating in Redis between runs."""
    yield
    for key in redis_client.scan_iter("token_blacklist:*"):
        redis_client.delete(key)


@pytest.fixture()
def register_and_get_token(client, db_session):
    """Registers a user and returns a valid access token for them.

    Usage:
        token = register_and_get_token("alice@example.com")
        token = register_and_get_token("admin@example.com", role="admin")

    Promoting to "admin" is done directly in the database, bypassing the
    real "an existing admin must promote you" flow — that flow is tested
    separately (see tests/users/), this fixture just needs a ready-made
    admin to set up other tests.
    """

    def _factory(email: str, role: str = "customer") -> str:
        client.post(
            "/api/v1/auth/register",
            json={"name": "Test User", "email": email, "password": "supersecret"},
        )
        user = db_session.query(User).filter(User.email == email).first()

        if role != "customer":
            role_obj = db_session.query(Role).filter(Role.name == role).first()
            user.role = role_obj
            db_session.commit()

        return create_access_token(subject=str(user.id))

    return _factory


@pytest.fixture()
def get_user_by_email(db_session):
    def _factory(email: str):
        user = db_session.query(User).filter(User.email == email).first()
        assert user is not None, f"No user found with email {email}"
        return user
    return _factory
