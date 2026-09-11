import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.core.database import Base, engine
import app.models

client = TestClient(fastapi_app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

def test_1_get_detection_rules():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/rules/", headers=headers)
    assert res.status_code == 200
    rules = res.json()
    assert isinstance(rules, list)
    assert len(rules) >= 7

def test_2_create_custom_detection_rule():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    new_rule = {
        "name": "Custom SSH Port Scanning Rule",
        "description": "Detects high-volume SSH port scan activity.",
        "category": "Discovery",
        "severity": "CRITICAL",
        "priority": "CRITICAL",
        "condition_field": "raw_message",
        "condition_operator": "contains",
        "condition_value": "port scan detected",
        "status": "ACTIVE"
    }

    res = client.post("/api/v1/rules/", json=new_rule, headers=headers)
    assert res.status_code == 200
    rule_data = res.json()
    assert rule_data["name"] == "Custom SSH Port Scanning Rule"
    assert rule_data["version"] == 1

def test_3_test_detection_rule():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    test_payload = {
        "rule": {
            "name": "Test Rule",
            "severity": "HIGH",
            "condition_field": "raw_message",
            "condition_operator": "contains",
            "condition_value": "unauthorized_sudo_attempt"
        },
        "test_log": {
            "raw_message": "User analyst executed unauthorized_sudo_attempt on SRV-01"
        }
    }

    res = client.post("/api/v1/rules/test", json=test_payload, headers=headers)
    assert res.status_code == 200
    result = res.json()
    assert result["result"] == "MATCH"

def test_4_rule_status_update_rbac():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Disable RULE-001
    res = client.patch("/api/v1/rules/RULE-001/status?status=DISABLED", headers=headers)
    assert res.status_code == 200
    assert res.json()["rule"]["status"] == "DISABLED"
