from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.schemas.organization import OrganizationCreate, OrganizationResponse, MemberCreate, MemberResponse
from app.services.tenant_service import tenant_service

router = APIRouter()

@router.get("/", response_model=List[OrganizationResponse])
def list_organizations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = tenant_service.get_user_org_id(db, current_user)
    return db.query(Organization).filter(Organization.id == org_id).all()

@router.post("/", response_model=OrganizationResponse)
def create_organization(org_in: OrganizationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["Admin", "SOC_ADMIN"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admins can create organizations.")

    try:
        new_org = tenant_service.create_organization(db, name=org_in.name, slug=org_in.slug)
        tenant_service.add_member(db, organization_id=new_org.id, user_id=current_user.id, role="OrgAdmin")
        return new_org
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/members", response_model=List[MemberResponse])
def list_org_members(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = tenant_service.get_user_org_id(db, current_user)
    return db.query(OrganizationMember).filter(OrganizationMember.organization_id == org_id).all()

@router.post("/members", response_model=MemberResponse)
def add_org_member(mem_in: MemberCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = tenant_service.get_user_org_id(db, current_user)
    return tenant_service.add_member(db, organization_id=org_id, user_id=mem_in.user_id, role=mem_in.role)
