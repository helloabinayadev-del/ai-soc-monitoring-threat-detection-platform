import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine
from app.seed import seed_database

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    seed_database()

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health/")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["status"] in ["HEALTHY", "DEGRADED"]
