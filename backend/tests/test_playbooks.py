import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.core.database import Base, engine
import app.models

client = TestClient(fastapi_app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

def test_1_get_playbooks_list():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/playbooks/", headers=headers)
    assert res.status_code == 200
    playbooks = res.json()
    assert isinstance(playbooks, list)
    assert len(playbooks) >= 3

def test_2_recommend_and_execute_playbook_workflow():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch active alerts
    alerts_res = client.get("/api/v1/alerts/", headers=headers)
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    assert len(alerts) > 0
    target_alert = alerts[0]

    # 2. Get playbook recommendation
    rec_res = client.get(f"/api/v1/playbooks/recommend/{target_alert['id']}", headers=headers)
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    assert "recommended_playbook" in rec_data
    pb_id = rec_data["recommended_playbook"]["id"]

    # 3. Execute recommended playbook
    exec_res = client.post("/api/v1/playbooks/execute", json={
        "playbook_id": pb_id,
        "alert_id": target_alert["id"]
    }, headers=headers)
    assert exec_res.status_code == 200
    exec_data = exec_res.json()
    assert "execution_id" in exec_data
    assert exec_data["status"] in ["COMPLETED", "PENDING_APPROVAL"]

    # 4. If human approval required, approve action
    if exec_data.get("requires_approval"):
        app_res = client.post("/api/v1/playbooks/approve", json={
            "execution_id": exec_data["execution_id"]
        }, headers=headers)
        assert app_res.status_code == 200
        assert app_res.json()["status"] == "COMPLETED"

def test_3_idempotent_playbook_execution():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    alerts_res = client.get("/api/v1/alerts/", headers=headers)
    target_alert = alerts_res.json()[0]

    # Execute PB-002 twice
    exec1 = client.post("/api/v1/playbooks/execute", json={"playbook_id": "PB-002", "alert_id": target_alert["id"]}, headers=headers)
    assert exec1.status_code == 200

    exec2 = client.post("/api/v1/playbooks/execute", json={"playbook_id": "PB-002", "alert_id": target_alert["id"]}, headers=headers)
    assert exec2.status_code == 200
    assert "Idempotent execution detected" in exec2.json()["message"]
