import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.core.database import Base, engine
from app.services.threat_intel_service import threat_intel_service
import app.models

client = TestClient(fastapi_app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

def test_1_ioc_validation_and_normalization():
    # IPv4
    val, ioc_type, is_valid = threat_intel_service.validate_and_normalize_ioc("198.51.100.45")
    assert is_valid is True
    assert ioc_type == "IPv4"
    assert val == "198.51.100.45"

    # Domain
    val, ioc_type, is_valid = threat_intel_service.validate_and_normalize_ioc("MALICIOUS-C2-DOMAIN.COM")
    assert is_valid is True
    assert ioc_type == "Domain"
    assert val == "malicious-c2-domain.com"

    # SHA256 Hash
    hash_str = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    val, ioc_type, is_valid = threat_intel_service.validate_and_normalize_ioc(hash_str)
    assert is_valid is True
    assert ioc_type == "SHA256"

    # Invalid string
    val, ioc_type, is_valid = threat_intel_service.validate_and_normalize_ioc("not_an_ioc")
    assert is_valid is False

def test_2_ioc_enrichment_endpoint_not_configured():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/intelligence/enrich/203.0.113.99", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["ioc_value"] == "203.0.113.99"
    assert data["ioc_type"] == "IPv4"
    assert data["result_state"] in ["NOT_CONFIGURED", "BENIGN", "MALICIOUS", "NO_DATA"]

def test_3_bulk_ioc_enrichment():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/v1/intelligence/enrich/bulk", json={
        "iocs": ["198.51.100.45", "example-c2.com", "invalid_ioc"]
    }, headers=headers)

    assert res.status_code == 200
    results = res.json()
    assert isinstance(results, list)
    assert len(results) == 3
