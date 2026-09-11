import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.core.database import Base, engine, SessionLocal
import app.models
from app.services.audit_service import audit_service

client = TestClient(fastapi_app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

def test_audit_service_recording():
    db = SessionLocal()
    try:
        entry = audit_service.record_action(
            db=db,
            actor_username="test_admin",
            action="TEST_ACTION",
            resource_type="TestResource",
            resource_id="101",
            status="SUCCESS",
            details="Unit test audit entry creation"
        )
        assert entry.id is not None
        assert entry.actor_username == "test_admin"
        assert entry.action == "TEST_ACTION"
    finally:
        db.close()
