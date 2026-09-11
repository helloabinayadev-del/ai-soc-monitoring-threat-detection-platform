from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.organization import Organization, OrganizationMember
from app.models.user import User

class TenantService:
    def get_or_create_default_org(self, db: Session) -> Organization:
        """Ensures Default Organization (org_id=1) exists for backward compatibility."""
        org = db.query(Organization).filter(Organization.id == 1).first()
        if not org:
            org = Organization(
                id=1,
                name="Default Organization",
                slug="default-org",
                status="ACTIVE"
            )
            db.add(org)
            db.commit()
            db.refresh(org)
        return org

    def create_organization(self, db: Session, name: str, slug: str) -> Organization:
        existing = db.query(Organization).filter((Organization.name == name) | (Organization.slug == slug)).first()
        if existing:
            raise ValueError(f"Organization '{name}' or slug '{slug}' already exists.")
        org = Organization(name=name, slug=slug, status="ACTIVE")
        db.add(org)
        db.commit()
        db.refresh(org)
        return org

    def add_member(self, db: Session, organization_id: int, user_id: int, role: str = "Analyst") -> OrganizationMember:
        member = db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id
        ).first()
        if not member:
            member = OrganizationMember(
                organization_id=organization_id,
                user_id=user_id,
                role=role
            )
            db.add(member)
            db.commit()
            db.refresh(member)
        return member

    def get_user_org_id(self, db: Session, user: User) -> int:
        """Resolves active organization ID for requesting authenticated user."""
        member = db.query(OrganizationMember).filter(OrganizationMember.user_id == user.id).first()
        if member:
            return member.organization_id
        # Fallback to Default Organization (org_id=1)
        self.get_or_create_default_org(db)
        self.add_member(db, organization_id=1, user_id=user.id, role=user.role or "Analyst")
        return 1

tenant_service = TenantService()
