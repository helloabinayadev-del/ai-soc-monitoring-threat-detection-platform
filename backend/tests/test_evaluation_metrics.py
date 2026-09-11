import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.core.database import Base, engine
import app.models

client = TestClient(fastapi_app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

def test_1_run_evaluation_pipeline_api():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/evaluation/run?n_samples=500", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "comparison_matrix" in data
    assert "soc_metrics" in data
    assert data["soc_metrics"]["mttd_seconds"]["aiml"] == 12.5

def test_2_get_latest_evaluation_api():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/evaluation/latest", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "comparison_matrix" in data or "dataset_info" in data

def test_3_get_analytics_summary_api():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/analytics/summary", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "total_logs" in data["metrics"]
