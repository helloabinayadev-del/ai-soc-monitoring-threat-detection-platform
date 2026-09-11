import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.ml.anomaly_detector import ml_anomaly_detector
from app.ml.feature_engineering import feature_extractor
from app.services.prioritization_service import prioritization_service
from app.ml.evaluation_pipeline import evaluation_pipeline

client = TestClient(app)

def test_ml_feature_extraction():
    log_dict = {
        "log_source": "WindowsEvent",
        "event_type": "Authentication",
        "source_ip": "192.168.1.100",
        "destination_ip": "10.0.0.5",
        "source_port": 49152,
        "destination_port": 445,
        "action": "FAIL",
        "severity": "HIGH",
        "raw_message": "EventID 4625: Account failed to log on."
    }
    vec = feature_extractor.extract_features(log_dict)
    assert vec.shape == (1, 10)

def test_ml_anomaly_detector_prediction():
    log_dict = {
        "log_source": "LinuxSyslog",
        "event_type": "PrivilegeEscalation",
        "source_ip": "10.0.4.12",
        "action": "EXECUTE",
        "severity": "CRITICAL",
        "raw_message": "sudo: user : TTY=pts/1 ; PWD=/tmp ; USER=root ; COMMAND=/bin/bash (root access privilege escalation)"
    }
    res = ml_anomaly_detector.predict(log_dict)
    assert "anomaly_score" in res
    assert "prediction" in res
    assert res["prediction"] in ["NORMAL", "ANOMALOUS"]
    assert "contributing_features" in res

def test_intelligent_prioritization_calculation():
    risk = prioritization_service.calculate_risk(
        severity="HIGH",
        anomaly_score=85.0,
        source_ip="192.168.1.105",
        affected_asset="DC-PRIMARY-01",
        threat_intel_match=True,
        correlated_event_count=3
    )
    assert risk["risk_score"] > 80.0
    assert risk["priority"] in ["HIGH", "CRITICAL"]
    assert len(risk["contributing_factors"]) > 0

def test_evaluation_pipeline_execution():
    res = evaluation_pipeline.run_evaluation(n_samples=500)
    assert "comparison_matrix" in res
    assert "soc_metrics" in res
    assert res["comparison_matrix"]["aiml_assisted"][0] > 0.50

def test_e2e_upgraded_log_ingest_and_correlation():
    # Login
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Ingest log
    ingest_res = client.post("/api/v1/logs/", json={
        "log_source": "WindowsEvent",
        "event_type": "Authentication",
        "source_ip": "198.51.100.99",
        "destination_ip": "10.0.0.5",
        "user_name": "target_user",
        "hostname": "DC-PRIMARY-01",
        "action": "FAIL",
        "severity": "HIGH",
        "raw_message": "EventID 4625: Account failed to log on. Invalid password attempt from 198.51.100.99"
    }, headers=headers)
    assert ingest_res.status_code == 200
    log_data = ingest_res.json()
    assert "correlation_id" in log_data

    # Query correlations API
    corr_res = client.get("/api/v1/correlations/", headers=headers)
    assert corr_res.status_code == 200
    assert len(corr_res.json()) > 0

    # Query evaluation API
    eval_res = client.get("/api/v1/evaluation/latest", headers=headers)
    assert eval_res.status_code == 200

    # Query Copilot 10-point evidence API
    cop_res = client.post("/api/v1/copilot/query", json={"query": "Analyze recent security alerts"}, headers=headers)
    assert cop_res.status_code == 200
    cop_json = cop_res.json()
    assert "answer" in cop_json
