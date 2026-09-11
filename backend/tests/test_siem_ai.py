import pytest
from app.ai.anomaly_detector import anomaly_detector
from app.ai.threat_classifier import threat_classifier
from app.services.copilot_service import copilot_service

def test_anomaly_detector_prediction():
    sample_normal_log = {
        "source_port": 49152,
        "destination_port": 443,
        "raw_message": "Standard TLS handshake to internal server",
        "action": "ALLOW"
    }
    is_anomaly, score = anomaly_detector.predict(sample_normal_log)
    assert is_anomaly in ["NORMAL", "ANOMALOUS"]
    assert 0.0 <= score <= 100.0

def test_threat_classifier_rules():
    raw_powershell_log = "CrowdStrike: powershell.exe -ExecutionPolicy Bypass -EncodedCommand SQBFA..."
    match = threat_classifier.classify_log(raw_powershell_log)
    assert match is not None
    assert match["rule_id"] == "RULE-003"
    assert match["category"] == "Execution"
    assert "PowerShell" in match["mitre_technique"]

def test_copilot_service_query():
    res = copilot_service.analyze_query("How do I contain a Cobalt Strike infection?")
    assert "containment actions" in res.answer.lower()
    assert len(res.action_items) > 0
    assert len(res.mitre_references) > 0
