import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.core.database import Base, engine
import app.models

client = TestClient(fastapi_app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

def test_1_create_case_and_attach_evidence_sha256():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Incident / Case
    inc_res = client.post("/api/v1/incidents/", json={
        "title": "Forensic Investigation - Unauthorized Access",
        "summary": "Investigating brute-force authentication attempt targeting DC-01",
        "severity": "HIGH"
    }, headers=headers)
    assert inc_res.status_code == 200
    inc_id = inc_res.json()["id"]

    # 2. Attach Evidence with SHA-256 Hash
    evd_res = client.post(f"/api/v1/incidents/{inc_id}/evidence", json={
        "evidence_type": "LOG_RECORD",
        "source": "WindowsEventID 4625",
        "raw_content": "An account failed to log on. Subject: Security ID: S-1-5-18 Account Name: DC-PRIMARY$"
    }, headers=headers)
    assert evd_res.status_code == 200
    evd_data = evd_res.json()
    assert "sha256_hash" in evd_data
    assert len(evd_data["sha256_hash"]) == 64

def test_2_generate_forensic_case_report():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create Case
    inc_res = client.post("/api/v1/incidents/", json={
        "title": "Case Investigation Report Test",
        "summary": "Generating forensic report for evidence audit",
        "severity": "CRITICAL"
    }, headers=headers)
    inc_id = inc_res.json()["id"]

    # Fetch Case Report
    rep_res = client.get(f"/api/v1/incidents/{inc_id}/report", headers=headers)
    assert rep_res.status_code == 200
    rep_data = rep_res.json()
    assert "sha256_report_hash" in rep_data
    assert len(rep_data["sha256_report_hash"]) == 64
    assert rep_data["ai_copilot_analysis"]["label"] == "AI-GENERATED CONTENT (GROUNDED RECOMMENDATIONS)"
