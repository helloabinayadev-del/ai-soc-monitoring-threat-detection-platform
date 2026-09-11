import pytest

import app.models  # noqa: F401 — register ORM models on Base.metadata
from app.core.database import Base, engine
from app.seed import seed_database


@pytest.fixture(scope="session", autouse=True)
def initialize_test_database():
    """Create all tables and seed demo data once per pytest session.

    GitHub Actions sets DATABASE_URL to PostgreSQL. Tests that do not call
    create_all() themselves (and TestClient without a lifespan context)
    otherwise hit UndefinedTable on relations such as log_events.
    """
    Base.metadata.create_all(bind=engine)
    try:
        seed_database()
    except Exception as exc:
        print(f"[!] Test database seed warning: {exc}")
    yield
