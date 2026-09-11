import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.ml.feature_engineering import feature_extractor, SecurityFeatureExtractor
from app.ml.preprocessing import preprocessor
from app.ml.anomaly_detector import ml_anomaly_detector
from app.ml.model_manager import model_manager

from app.core.database import Base, engine
import app.models

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

client = TestClient(fastapi_app)

def test_1_feature_extraction():
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
    assert len(SecurityFeatureExtractor.FEATURE_NAMES) == 10

def test_2_preprocessing_scaling():
    log_dict = {
        "log_source": "LinuxSyslog",
        "event_type": "Authentication",
        "source_ip": "10.0.0.1",
        "action": "ALLOW",
        "severity": "INFORMATIONAL",
        "raw_message": "Session opened for user admin"
    }
    vec = feature_extractor.extract_features(log_dict)
    scaled = preprocessor.transform(vec)
    assert scaled.shape == (1, 10)

def test_3_model_status_and_loading():
    status = model_manager.get_model_status()
    assert status["model_name"] == "IsolationForest"
    assert status["is_fitted"] is True
    assert status["n_estimators"] == 100
    assert status["features_count"] == 10

def test_4_model_prediction_normal_vs_anomalous():
    normal_log = {
        "log_source": "Firewall",
        "event_type": "NetworkConnection",
        "source_ip": "10.0.0.15",
        "destination_ip": "10.0.0.5",
        "source_port": 50123,
        "destination_port": 443,
        "action": "ALLOW",
        "severity": "INFORMATIONAL",
        "raw_message": "Outbound HTTPS session established"
    }
    res_normal = ml_anomaly_detector.predict(normal_log)
    assert res_normal["prediction"] in ["NORMAL", "ANOMALOUS"]
    assert "anomaly_score" in res_normal
    assert "contributing_features" in res_normal

    suspicious_log = {
        "log_source": "EndpointEDR",
        "event_type": "PrivilegeEscalation",
        "source_ip": "192.168.1.250",
        "destination_ip": "10.0.0.5",
        "source_port": 65432,
        "destination_port": 22,
        "action": "EXECUTE",
        "severity": "CRITICAL",
        "raw_message": "sudo: developer : TTY=pts/1 ; USER=root ; COMMAND=/bin/bash (root access privilege escalation)"
    }
    res_suspicious = ml_anomaly_detector.predict(suspicious_log)
    assert res_suspicious["anomaly_score"] >= 0.0
    assert "model_version" in res_suspicious

def test_5_threshold_behavior_configuration():
    # Update threshold via API/Manager
    new_t = model_manager.update_threshold(50.0)
    assert new_t == 50.0
    assert ml_anomaly_detector.threshold == 50.0

    # Reset back to default
    model_manager.update_threshold(65.0)

def test_6_api_endpoints_analyze_and_results():
    # Login for Auth
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test POST /api/v1/ml/analyze
    analyze_res = client.post("/api/v1/ml/analyze", json={
        "raw_message": "EventID 4625: Account failed to log on (failed login attempt)",
        "source_ip": "192.168.1.105",
        "action": "FAIL",
        "severity": "HIGH"
    }, headers=headers)
    assert analyze_res.status_code == 200
    assert "anomaly_score" in analyze_res.json()

    # Test GET /api/v1/ml/status
    status_res = client.get("/api/v1/ml/status", headers=headers)
    assert status_res.status_code == 200
    assert status_res.json()["is_fitted"] is True

    # Test GET /api/v1/ml/results
    results_res = client.get("/api/v1/ml/results", headers=headers)
    assert results_res.status_code == 200
    assert isinstance(results_res.json(), list)

def test_7_e2e_log_ingest_persistence_and_siem_integration():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Ingest Log
    log_res = client.post("/api/v1/logs/", json={
        "log_source": "EndpointEDR",
        "event_type": "ProcessCreation",
        "source_ip": "10.0.2.88",
        "destination_ip": "10.0.2.88",
        "source_port": 0,
        "destination_port": 0,
        "user_name": "SYSTEM",
        "hostname": "DC-PRIMARY-01",
        "action": "EXECUTE",
        "severity": "HIGH",
        "raw_message": "powershell.exe -ExecutionPolicy Bypass -EncodedCommand SQBFAAX... (downloadstring iex bypass)"
    }, headers=headers)
    assert log_res.status_code == 200
    log_data = log_res.json()
    assert log_data["is_anomaly"] in ["NORMAL", "ANOMALOUS"]
    assert log_data["anomaly_score"] >= 0.0

    # 2. Check SecurityAlert created with detection_source
    alerts_res = client.get("/api/v1/alerts/", headers=headers)
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    assert len(alerts) > 0
    recent_alert = alerts[0]
    assert "detection_source" in recent_alert
    assert recent_alert["detection_source"] in ["RULE_BASED", "ML_ANOMALY", "HYBRID"]

    # 3. Verify MLPrediction persisted record in DB via API
    ml_preds_res = client.get("/api/v1/ml/results", headers=headers)
    assert ml_preds_res.status_code == 200
    preds = ml_preds_res.json()
    assert len(preds) > 0
    assert "anomaly_score" in preds[0]
