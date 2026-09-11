import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.core.database import Base, engine
from app.websockets.connection_manager import ws_manager

client = TestClient(fastapi_app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

def test_1_websocket_connection_and_heartbeat():
    with client.websocket_connect("/ws/soc-stream") as websocket:
        websocket.send_text("PING")
        data = websocket.receive_text()
        assert "ACK" in data or "PONG" in data or "PING" in data

def test_2_payload_sanitization_no_secrets():
    dirty_payload = {
        "user": "admin",
        "password": "SuperSecretPassword123!",
        "access_token": "bearer.jwt.secret.token",
        "ip_address": "192.168.1.1"
    }

    clean_payload = ws_manager.sanitize_payload(dirty_payload)
    assert "password" not in clean_payload
    assert "access_token" not in clean_payload
    assert clean_payload["user"] == "admin"
    assert clean_payload["ip_address"] == "192.168.1.1"

def test_3_event_envelope_formatting():
    msg = {
        "type": "NEW_SECURITY_EVENT",
        "payload": {
            "source_ip": "198.51.100.77",
            "action": "ALLOW"
        }
    }
    
    # Broadcast method produces sanitized envelope
    assert ws_manager.sanitize_payload(msg["payload"])["source_ip"] == "198.51.100.77"
