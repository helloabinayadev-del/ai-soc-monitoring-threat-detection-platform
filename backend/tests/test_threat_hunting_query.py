import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.core.database import Base, engine
from app.services.threat_hunting_engine import threat_hunting_engine
import app.models

client = TestClient(fastapi_app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

def test_1_execute_safe_hunt_query(db_session=None):
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        res = threat_hunting_engine.execute_safe_hunt(
            db=db,
            search="failed login",
            severity="HIGH"
        )
        assert "events" in res
        assert "total_matches" in res
        assert res["query_parameters"]["search"] == "failed login"
    finally:
        db.close()

def test_2_sql_injection_prevention():
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        with pytest.raises(ValueError, match="SQL keyword detected"):
            threat_hunting_engine.execute_safe_hunt(
                db=db,
                search="admin'; DROP TABLE log_events;--"
            )
    finally:
        db.close()

def test_3_ai_natural_language_to_query():
    nl_res = threat_hunting_engine.ai_natural_language_hunt("Find repeated failed authentication attempts")
    assert "generated_safe_parameters" in nl_res
    params = nl_res["generated_safe_parameters"]
    assert params["event_type"] == "Authentication"
    assert params["search"] == "failed login"

def test_4_saved_hunts():
    saved = threat_hunting_engine.save_hunt(
        name="Custom C2 Hunt",
        description="Hunt for outbound HTTPS beacons",
        query={"search": "c2 server"}
    )
    assert "id" in saved
    assert len(threat_hunting_engine.saved_hunts) >= 3
