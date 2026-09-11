import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.services.tenant_service import tenant_service

client = TestClient(fastapi_app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Ensure Default Admin exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@socplatform.com",
                hashed_password=get_password_hash("Admin@123"),
                full_name="SOC Administrator",
                role="Admin"
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
        
        # Ensure Default Org exists
        tenant_service.get_or_create_default_org(db)
        tenant_service.get_user_org_id(db, admin_user)
    finally:
        db.close()

def test_1_multi_tenant_organization_isolation():
    # Login Admin
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch User's Active Organization
    orgs_res = client.get("/api/v1/organizations/", headers=headers)
    assert orgs_res.status_code == 200
    orgs = orgs_res.json()
    assert len(orgs) > 0
    assert orgs[0]["name"] == "Default Organization"

def test_2_create_new_organization():
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    unique_slug = f"acme-soc-{uuid.uuid4().hex[:8]}"
    create_res = client.post("/api/v1/organizations/", json={
        "name": f"Acme Corp SOC {unique_slug}",
        "slug": unique_slug
    }, headers=headers)
    assert create_res.status_code == 200, create_res.text
    new_org = create_res.json()
    assert new_org["slug"] == unique_slug

def test_3_idor_cross_tenant_access_block():
    # Attempting to fetch non-existent or cross-tenant incident
    login_res = client.post("/api/v1/auth/token", data={"username": "admin", "password": "Admin@123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    inc_res = client.get("/api/v1/incidents/999999", headers=headers)
    assert inc_res.status_code == 404
