import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.core.database import Base, engine
import app.models

client = TestClient(fastapi_app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

def test_1_get_mitre_coverage_matrix():
    res = client.get("/api/v1/mitre/coverage")
    assert res.status_code == 200
    data = res.json()
    assert "attack_version" in data
    assert "coverage_percentage" in data
    assert isinstance(data["coverage_matrix"], list)
    assert len(data["coverage_matrix"]) == 14

def test_2_get_attack_chain_analysis():
    res = client.get("/api/v1/mitre/attack-chain")
    assert res.status_code == 200
    data = res.json()
    assert "chain_classification" in data
    assert "tactical_progression" in data
    assert isinstance(data["tactical_progression"], list)
