import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.core.database import Base, engine
import app.models

client = TestClient(fastapi_app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

def test_complete_master_soc_pipeline():
    # 1. Authentication
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Log Ingestion & Normalization + ML Anomaly + Detection + Risk + Correlation
    ingest_res = client.post("/api/v1/logs/", json={
        "log_source": "Firewall",
        "event_type": "Authentication",
        "source_ip": "198.51.100.99",
        "destination_ip": "10.0.0.5",
        "source_port": 50123,
        "destination_port": 445,
        "user_name": "admin",
        "hostname": "DC-PRIMARY-01",
        "action": "FAIL",
        "severity": "HIGH",
        "raw_message": "EventID 4625: Account failed to log on (failed login attempt brute force)"
    }, headers=headers)
    assert ingest_res.status_code == 200
    log_id = ingest_res.json()["id"]

    # 3. SIEM Alerts
    alerts_res = client.get("/api/v1/alerts/", headers=headers)
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    assert len(alerts) > 0
    target_alert = alerts[0]

    # 4. Threat Intelligence IOC Enrichment
    intel_res = client.get(f"/api/v1/intelligence/enrich/{target_alert['source_ip']}", headers=headers)
    assert intel_res.status_code == 200
    assert intel_res.json()["ioc_value"] == target_alert["source_ip"]

    # 5. MITRE ATT&CK Coverage & Chain
    mitre_res = client.get("/api/v1/mitre/coverage", headers=headers)
    assert mitre_res.status_code == 200

    # 6. Case Management & Evidence Attachment with SHA-256 Hash
    inc_res = client.post("/api/v1/incidents/", json={
        "title": "Master E2E Pipeline Incident Case",
        "summary": f"Linked to alert #{target_alert['id']}",
        "severity": "HIGH"
    }, headers=headers)
    assert inc_res.status_code == 200
    inc_id = inc_res.json()["id"]

    evd_res = client.post(f"/api/v1/incidents/{inc_id}/evidence", json={
        "evidence_type": "LOG_RECORD",
        "source": "LogEvent ID #" + str(log_id),
        "raw_content": f"EventID 4625 raw log telemetry for log #{log_id}"
    }, headers=headers)
    assert evd_res.status_code == 200
    assert len(evd_res.json()["sha256_hash"]) == 64

    # 7. SOAR Response Playbook Execution & Approval
    pb_res = client.post("/api/v1/playbooks/execute", json={
        "playbook_id": "PB-001",
        "alert_id": target_alert["id"]
    }, headers=headers)
    assert pb_res.status_code == 200

    # 8. Report Generation with SHA-256 Report Checksum
    rep_res = client.get(f"/api/v1/incidents/{inc_id}/report", headers=headers)
    assert rep_res.status_code == 200
    assert len(rep_res.json()["sha256_report_hash"]) == 64

    # 9. Audit Logging Verification
    audit_res = client.get("/api/v1/audit/", headers=headers)
    assert audit_res.status_code == 200
    assert len(audit_res.json()) > 0
