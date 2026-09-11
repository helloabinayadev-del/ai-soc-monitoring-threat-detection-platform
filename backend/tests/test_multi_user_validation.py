import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.models.log import LogEvent
from app.models.alert import SecurityAlert
from app.models.incident import Incident
from app.core.security import get_password_hash
from app.services.tenant_service import tenant_service

client = TestClient(fastapi_app)

@pytest.fixture(autouse=True)
def setup_multi_tenant_env():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 1. Ensure Default Org A (ID 1)
        org_a = tenant_service.get_or_create_default_org(db)

        # 2. Create Org B
        org_b = db.query(Organization).filter(Organization.slug == "org-b-cybershield").first()
        if not org_b:
            org_b = Organization(name="CyberShield Incident Response", slug="org-b-cybershield", status="ACTIVE")
            db.add(org_b)
            db.commit()
            db.refresh(org_b)

        # 3. Create Users
        # User A1: Admin Org A
        user_a1 = db.query(User).filter(User.username == "admin_org_a").first()
        if not user_a1:
            user_a1 = User(username="admin_org_a", email="admin.a@orga.com", hashed_password=get_password_hash("PassA1!"), role="Admin")
            db.add(user_a1)
            db.commit()
            db.refresh(user_a1)
            tenant_service.add_member(db, organization_id=org_a.id, user_id=user_a1.id, role="OrgAdmin")

        # User A2: Analyst Org A
        user_a2 = db.query(User).filter(User.username == "analyst_org_a").first()
        if not user_a2:
            user_a2 = User(username="analyst_org_a", email="analyst.a@orga.com", hashed_password=get_password_hash("PassA2!"), role="Analyst")
            db.add(user_a2)
            db.commit()
            db.refresh(user_a2)
            tenant_service.add_member(db, organization_id=org_a.id, user_id=user_a2.id, role="Analyst")

        # User A3: Viewer Org A
        user_a3 = db.query(User).filter(User.username == "viewer_org_a").first()
        if not user_a3:
            user_a3 = User(username="viewer_org_a", email="viewer.a@orga.com", hashed_password=get_password_hash("PassA3!"), role="Auditor")
            db.add(user_a3)
            db.commit()
            db.refresh(user_a3)
            tenant_service.add_member(db, organization_id=org_a.id, user_id=user_a3.id, role="Viewer")

        # User B1: Admin Org B
        user_b1 = db.query(User).filter(User.username == "admin_org_b").first()
        if not user_b1:
            user_b1 = User(username="admin_org_b", email="admin.b@orgb.com", hashed_password=get_password_hash("PassB1!"), role="Admin")
            db.add(user_b1)
            db.commit()
            db.refresh(user_b1)
            tenant_service.add_member(db, organization_id=org_b.id, user_id=user_b1.id, role="OrgAdmin")

        # User B2: Analyst Org B
        user_b2 = db.query(User).filter(User.username == "analyst_org_b").first()
        if not user_b2:
            user_b2 = User(username="analyst_org_b", email="analyst.b@orgb.com", hashed_password=get_password_hash("PassB2!"), role="Analyst")
            db.add(user_b2)
            db.commit()
            db.refresh(user_b2)
            tenant_service.add_member(db, organization_id=org_b.id, user_id=user_b2.id, role="Analyst")

        # 4. Seed Tenant-Owned Incidents
        inc_a = db.query(Incident).filter(Incident.incident_number == "INC-ORG-A-001").first()
        if not inc_a:
            inc_a = Incident(incident_number="INC-ORG-A-001", title="Org A Incident Case", summary="Org A Security Ticket", severity="HIGH", status="OPEN", organization_id=org_a.id)
            db.add(inc_a)
            db.commit()

        inc_b = db.query(Incident).filter(Incident.incident_number == "INC-ORG-B-001").first()
        if not inc_b:
            inc_b = Incident(incident_number="INC-ORG-B-001", title="Org B Incident Case", summary="Org B Security Ticket", severity="CRITICAL", status="OPEN", organization_id=org_b.id)
            db.add(inc_b)
            db.commit()

    finally:
        db.close()

def test_1_authentication_scenarios():
    # Valid Login
    res = client.post("/api/v1/auth/token", data={"username": "admin_org_a", "password": "PassA1!"})
    assert res.status_code == 200
    assert "access_token" in res.json()

    # Invalid Password
    res_bad_pwd = client.post("/api/v1/auth/token", data={"username": "admin_org_a", "password": "WrongPassword!"})
    assert res_bad_pwd.status_code == 401

    # Protected Endpoint Without Token
    res_no_auth = client.get("/api/v1/incidents/")
    assert res_no_auth.status_code == 401

def test_2_tenant_data_isolation():
    # User A1 logs in
    login_a = client.post("/api/v1/auth/token", data={"username": "admin_org_a", "password": "PassA1!"})
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Fetch Incidents for User A
    res_a = client.get("/api/v1/incidents/", headers=headers_a)
    assert res_a.status_code == 200
    incidents_a = res_a.json()
    # User A must only see Org A incidents (org_id 1)
    for inc in incidents_a:
        assert inc.get("organization_id", 1) == 1

def test_3_idor_cross_tenant_prevention():
    # User A1 attempts to access Org B incident
    login_a = client.post("/api/v1/auth/token", data={"username": "admin_org_a", "password": "PassA1!"})
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    db = SessionLocal()
    inc_b = db.query(Incident).filter(Incident.incident_number == "INC-ORG-B-001").first()
    db.close()

    assert inc_b is not None

    # Requesting Org B incident ID as User A MUST return 404 (or 403)
    res_idor = client.get(f"/api/v1/incidents/{inc_b.id}", headers=headers_a)
    assert res_idor.status_code in [403, 404]

def test_4_rbac_privileged_action_protection():
    # User A3 (Viewer/Auditor) attempts Admin action (create organization)
    login_v = client.post("/api/v1/auth/token", data={"username": "viewer_org_a", "password": "PassA3!"})
    token_v = login_v.json()["access_token"]
    headers_v = {"Authorization": f"Bearer {token_v}"}

    res_create_org = client.post("/api/v1/organizations/", json={"name": "Forbidden Org", "slug": "forbidden"}, headers=headers_v)
    assert res_create_org.status_code == 403

def test_5_soar_authorization_check():
    # Analyst executes SOAR playbook action
    login_an = client.post("/api/v1/auth/token", data={"username": "analyst_org_a", "password": "PassA2!"})
    token_an = login_an.json()["access_token"]
    headers_an = {"Authorization": f"Bearer {token_an}"}

    pb_res = client.post("/api/v1/playbooks/execute", json={"playbook_id": "PB-001", "alert_id": 1}, headers=headers_an)
    assert pb_res.status_code == 200
    assert pb_res.json()["status"] in ["PENDING_APPROVAL", "EXECUTED", "SIMULATED"]
