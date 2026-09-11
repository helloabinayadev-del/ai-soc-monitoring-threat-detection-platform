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
    seed_database()

def test_rbac_unauthorized_access():
    # Attempting to access protected endpoint without token must return 401
    res = client.get("/api/v1/audit/")
    assert res.status_code == 401, f"Expected 401, got {res.status_code}"

def test_rbac_admin_authorized_access():
    # Login as admin
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Access audit logs with Admin token
    res = client.get("/api/v1/audit/", headers=headers)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    assert isinstance(res.json(), list)
