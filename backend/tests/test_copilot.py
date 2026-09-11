import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.core.database import Base, engine
import app.models

client = TestClient(fastapi_app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

def test_copilot_general_query():
    res = client.post("/api/v1/copilot/query", json={"query": "Explain brute force attack remediation"})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "action_items" in data
    assert data["confidence_score"] > 0.5

def test_copilot_alert_context_query():
    res = client.post("/api/v1/copilot/query", json={"query": "Analyze alert", "context_alert_id": 1})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "analysis_details" in data
