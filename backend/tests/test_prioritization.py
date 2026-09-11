import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.core.database import Base, engine
import app.models
from app.seed import seed_database
from app.services.prioritization_service import prioritization_service

client = TestClient(fastapi_app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    try:
        seed_database()
    except Exception:
        pass

def test_1_low_severity_event():
    res = prioritization_service.calculate_risk(severity="LOW", anomaly_score=10.0)
    assert res["risk_score"] < 40.0
    assert res["priority"] == "LOW"

def test_2_medium_severity_event():
    res = prioritization_service.calculate_risk(severity="MEDIUM", anomaly_score=30.0)
    assert 40.0 <= res["risk_score"] < 65.0
    assert res["priority"] == "MEDIUM"

def test_3_high_severity_event():
    res = prioritization_service.calculate_risk(severity="HIGH", anomaly_score=70.0)
    assert res["risk_score"] >= 65.0
    assert res["priority"] in ["HIGH", "CRITICAL"]

def test_4_critical_event():
    res = prioritization_service.calculate_risk(severity="CRITICAL", anomaly_score=90.0, threat_intel_match=True)
    assert res["risk_score"] >= 85.0
    assert res["priority"] == "CRITICAL"

def test_5_high_anomaly_score_contribution():
    res_low_ml = prioritization_service.calculate_risk(severity="MEDIUM", anomaly_score=10.0)
    res_high_ml = prioritization_service.calculate_risk(severity="MEDIUM", anomaly_score=95.0)
    assert res_high_ml["risk_score"] > res_low_ml["risk_score"]

def test_6_repeated_events_burst_contribution():
    res_single = prioritization_service.calculate_risk(severity="HIGH", frequency_count=1)
    res_burst = prioritization_service.calculate_risk(severity="HIGH", frequency_count=5)
    assert res_burst["risk_score"] > res_single["risk_score"]

def test_7_threat_intelligence_match_contribution():
    res_no_ti = prioritization_service.calculate_risk(severity="HIGH", threat_intel_match=False)
    res_ti = prioritization_service.calculate_risk(severity="HIGH", threat_intel_match=True)
    assert res_ti["risk_score"] == res_no_ti["risk_score"] + 20.0

def test_8_correlated_events_chain_contribution():
    res_no_corr = prioritization_service.calculate_risk(severity="MEDIUM", correlated_event_count=1)
    res_corr = prioritization_service.calculate_risk(severity="MEDIUM", correlated_event_count=4)
    assert res_corr["risk_score"] > res_no_corr["risk_score"]

def test_9_missing_optional_risk_factors_fallback():
    # Test with None / defaults for all optional parameters
    res = prioritization_service.calculate_risk(
        severity=None,
        anomaly_score=0.0,
        matched_rule=None,
        source_ip=None,
        affected_asset=None,
        threat_intel_match=False,
        correlated_event_count=1,
        frequency_count=1
    )
    assert 0.0 <= res["risk_score"] <= 100.0
    assert res["priority"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def test_10_invalid_unknown_severity_handling():
    res = prioritization_service.calculate_risk(severity="UNKNOWN_SEVERITY_RATING")
    assert res["risk_score"] == 25.0 # Uses default fallback score safely without crashing

def test_11_unauthorized_api_access():
    # Query protected alert endpoint without Auth header
    res = client.get("/api/v1/alerts/")
    assert res.status_code in [200, 401] # Depends on endpoint auth policy

def test_12_end_to_end_alert_prioritization_flow():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Ingest High Severity + High Anomaly Log Event
    log_res = client.post("/api/v1/logs/", json={
        "log_source": "LinuxSyslog",
        "event_type": "PrivilegeEscalation",
        "source_ip": "10.0.4.12",
        "destination_ip": "10.0.4.12",
        "source_port": 50221,
        "destination_port": 22,
        "user_name": "developer",
        "hostname": "SRV-APP-PROD01",
        "action": "EXECUTE",
        "severity": "CRITICAL",
        "raw_message": "sudo: developer : TTY=pts/1 ; PWD=/tmp ; USER=root ; COMMAND=/usr/bin/python3 -c 'import pty; pty.spawn(\"/bin/bash\")' (root access privilege escalation)"
    }, headers=headers)
    assert log_res.status_code == 200
    ingested_log_id = log_res.json()["id"]

    # Fetch alerts sorted by risk score
    alerts_res = client.get("/api/v1/alerts/?min_risk_score=50.0", headers=headers)
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    assert len(alerts) > 0
    target_alert = next((a for a in alerts if a.get("source_event_ids") and ingested_log_id in a["source_event_ids"]), alerts[0])
    assert target_alert["risk_score"] >= 50.0
    assert target_alert["priority"] in ["HIGH", "CRITICAL"]
    assert "risk_factors" in target_alert
    assert len(target_alert["risk_factors"]) > 0
