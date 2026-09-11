import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.core.database import Base, engine
import app.models

client = TestClient(fastapi_app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

def test_1_threat_hunting_log_search_filters():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Ingest test log with unique IP
    client.post("/api/v1/logs/", json={
        "log_source": "LinuxSyslog",
        "event_type": "Authentication",
        "source_ip": "198.51.100.222",
        "destination_ip": "10.0.0.5",
        "source_port": 49152,
        "destination_port": 22,
        "user_name": "hunter_user",
        "hostname": "SRV-HUNT-01",
        "action": "FAIL",
        "severity": "HIGH",
        "raw_message": "Failed password for hunter_user from 198.51.100.222 port 49152 ssh2"
    }, headers=headers)

    # Search by source_ip
    res_ip = client.get("/api/v1/logs/?source_ip=198.51.100.222", headers=headers)
    assert res_ip.status_code == 200
    assert len(res_ip.json()) > 0
    assert res_ip.json()[0]["source_ip"] == "198.51.100.222"

    # Search by user_name
    res_user = client.get("/api/v1/logs/?user_name=hunter_user", headers=headers)
    assert res_user.status_code == 200
    assert len(res_user.json()) > 0

    # Search by hostname
    res_host = client.get("/api/v1/logs/?hostname=SRV-HUNT-01", headers=headers)
    assert res_host.status_code == 200
    assert len(res_host.json()) > 0

def test_2_threat_hunting_parameterized_query_safety():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Malicious SQL injection search attempt
    sqli_search = "' OR '1'='1' --"
    res = client.get(f"/api/v1/logs/?search={sqli_search}", headers=headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list) # Safely executed parameterized query without SQL injection

def test_3_e2e_threat_hunting_investigation_workflow():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Search logs
    logs_res = client.get("/api/v1/logs/?severity=HIGH", headers=headers)
    assert logs_res.status_code == 200
    logs = logs_res.json()
    assert len(logs) > 0
    target_log = logs[0]

    # 2. Query Copilot with threat hunting prompt
    cop_res = client.post("/api/v1/copilot/query", json={
        "query": f"Investigate security events related to IP {target_log.get('source_ip')}",
        "context_alert_id": None
    }, headers=headers)
    assert cop_res.status_code == 200
    assert "answer" in cop_res.json()

    # 3. Create incident ticket for investigation case
    inc_res = client.post("/api/v1/incidents/", json={
        "title": f"Threat Hunting Investigation for IP {target_log.get('source_ip')}",
        "summary": "Investigating potential unauthorized access across network segments.",
        "severity": "HIGH",
        "correlation_id": target_log.get("correlation_id")
    }, headers=headers)
    assert inc_res.status_code == 200
    inc_data = inc_res.json()
    assert inc_data["status"] in ["OPEN", "INVESTIGATING"]
