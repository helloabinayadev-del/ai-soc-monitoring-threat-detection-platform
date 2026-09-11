import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_complete_e2e_attack_pipeline():
    # 1. Login
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Ingest Log Event
    log_res = client.post("/api/v1/logs/", json={
        "log_source": "WindowsEvent",
        "event_type": "Authentication",
        "source_ip": "192.168.1.200",
        "destination_ip": "10.0.0.5",
        "user_name": "target.user",
        "hostname": "WKSTN-FIN-09",
        "action": "FAIL",
        "severity": "HIGH",
        "raw_message": "EventID 4625: Account failed to log on. Invalid password attempt from 192.168.1.200 (failed login attempt)"
    }, headers=headers)
    assert log_res.status_code == 200
    log_id = log_res.json()["id"]

    # 3. Simulate Threat Scenario (Brute Force)
    sc_res = client.post("/api/v1/logs/simulate-scenario?scenario_type=brute_force", headers=headers)
    assert sc_res.status_code == 200

    # 4. Verify SIEM Alerts
    alerts_res = client.get("/api/v1/alerts/", headers=headers)
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    assert len(alerts) > 0

    # 5. Create Incident
    inc_res = client.post("/api/v1/incidents/", json={
        "title": "E2E Test Incident",
        "summary": "Brute force attack pipeline integration test",
        "severity": "HIGH",
        "assignee": "SOC Lead Administrator",
        "affected_systems": ["WKSTN-FIN-09"],
        "mitre_tactics": ["TA0006 - Credential Access"]
    }, headers=headers)
    assert inc_res.status_code == 200
    inc_id = inc_res.json()["id"]

    # 6. Execute SOAR Containment Playbook Action
    cont_res = client.post(f"/api/v1/incidents/{inc_id}/containment-action?action_type=ISOLATE_HOST", headers=headers)
    assert cont_res.status_code == 200

    # 7. Check Analytics Summary
    analytics_res = client.get("/api/v1/analytics/summary", headers=headers)
    assert analytics_res.status_code == 200
    metrics = analytics_res.json()["metrics"]
    assert metrics["total_logs"] > 0
    assert metrics["total_alerts"] > 0
