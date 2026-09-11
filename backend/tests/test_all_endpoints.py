import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.core.database import Base, engine
import app.models
from app.seed import seed_database

client = TestClient(fastapi_app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    try:
        seed_database()
    except Exception:
        pass


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    try:
        seed_database()
    except Exception:
        pass

def test_all_endpoints():
    print("\n--- AUDITING ALL ENDPOINTS ---")
    endpoints = [
        ("GET", "/"),
        ("GET", "/api/v1/health/"),
        ("GET", "/api/v1/logs/"),
        ("GET", "/api/v1/logs/?source=WindowsEvent&severity=HIGH&anomaly_only=true&search=admin"),
        ("GET", "/api/v1/alerts/"),
        ("GET", "/api/v1/alerts/1"),
        ("GET", "/api/v1/alerts/99999"), # Expect 404, NOT 500
        ("GET", "/api/v1/incidents/"),
        ("GET", "/api/v1/incidents/1"),
        ("GET", "/api/v1/incidents/99999"), # Expect 404, NOT 500
        ("GET", "/api/v1/intelligence/"),
        ("GET", "/api/v1/intelligence/lookup/198.51.100.45"),
        ("GET", "/api/v1/intelligence/lookup/nonexistent.ip.123"), # Expect 404, NOT 500
        ("GET", "/api/v1/intelligence/cve/CVE-2023-38606"),
        ("GET", "/api/v1/analytics/summary"),
    ]

    for method, url in endpoints:
        if method == "GET":
            res = client.get(url)
            print(f"[{res.status_code}] GET {url}")
            assert res.status_code != 500, f"HTTP 500 SERVER ERROR on GET {url}: {res.text}"

    # Test POST /copilot/query
    res_copilot = client.post("/api/v1/copilot/query", json={"query": "Explain critical alert on DC-PRIMARY-01"})
    print(f"[{res_copilot.status_code}] POST /api/v1/copilot/query")
    assert res_copilot.status_code != 500, f"HTTP 500 on Copilot query: {res_copilot.text}"

    # Test POST /logs/
    res_log = client.post("/api/v1/logs/", json={
        "log_source": "Firewall",
        "event_type": "NetworkConnection",
        "raw_message": "PaloAlto FW: Outbound session to 198.51.100.45:443",
        "source_ip": "10.0.1.50",
        "destination_ip": "198.51.100.45",
        "source_port": 54312,
        "destination_port": 443,
        "action": "ALLOW",
        "severity": "HIGH"
    })
    print(f"[{res_log.status_code}] POST /api/v1/logs/")
    assert res_log.status_code != 500, f"HTTP 500 on Log ingestion: {res_log.text}"

    # Test POST /incidents/1/containment-action
    res_action = client.post("/api/v1/incidents/1/containment-action?action_type=ISOLATE_HOST")
    print(f"[{res_action.status_code}] POST /api/v1/incidents/1/containment-action")
    assert res_action.status_code != 500, f"HTTP 500 on Containment Action: {res_action.text}"
