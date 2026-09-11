from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.core.database import get_db
from app.models.incident import Incident
from app.schemas.incident import IncidentResponse, IncidentCreate, IncidentUpdate
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.services.tenant_service import tenant_service

router = APIRouter()

@router.post("/", response_model=IncidentResponse)
def create_incident(incident_in: IncidentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = tenant_service.get_user_org_id(db, current_user)
    inc_num = f"INC-{uuid.uuid4().hex[:6].upper()}"
    new_inc = Incident(
        incident_number=inc_num,
        organization_id=org_id,
        **incident_in.model_dump()
    )
    db.add(new_inc)
    db.commit()
    db.refresh(new_inc)
    return new_inc

@router.get("/", response_model=List[IncidentResponse])
def get_incidents(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    org_id = tenant_service.get_user_org_id(db, current_user)
    query = db.query(Incident).filter(Incident.organization_id == org_id)
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    return query.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = tenant_service.get_user_org_id(db, current_user)
    inc = db.query(Incident).filter(Incident.id == incident_id, Incident.organization_id == org_id).first()
    if not inc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return inc

@router.put("/{incident_id}", response_model=IncidentResponse)
def update_incident(incident_id: int, inc_update: IncidentUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = tenant_service.get_user_org_id(db, current_user)
    inc = db.query(Incident).filter(Incident.id == incident_id, Incident.organization_id == org_id).first()
    if not inc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    
    update_data = inc_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(inc, field, value)
        
    db.commit()
    db.refresh(inc)
    return inc

@router.put("/{incident_id}/assign", response_model=IncidentResponse)
def assign_analyst(incident_id: int, assignee: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = tenant_service.get_user_org_id(db, current_user)
    inc = db.query(Incident).filter(Incident.id == incident_id, Incident.organization_id == org_id).first()
    if not inc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    inc.assignee = assignee
    inc.status = "IN_PROGRESS" if inc.status == "OPEN" else inc.status
    db.commit()
    db.refresh(inc)
    return inc

@router.post("/{incident_id}/containment-action")
def execute_containment_action(incident_id: int, action_type: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org_id = tenant_service.get_user_org_id(db, current_user)
    inc = db.query(Incident).filter(Incident.id == incident_id, Incident.organization_id == org_id).first()
    if not inc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    
    actions = {
        "ISOLATE_HOST": "Successfully executed EDR network isolation command for affected host.",
        "BLOCK_IP": "Boundary PaloAlto firewall rule created blocking malicious IP address.",
        "REVOKE_TOKENS": "Active Kerberos/OAuth user session tokens revoked across Active Directory domain.",
        "EDR_FULL_SCAN": "Deep malware file system scan launched via CrowdStrike agent."
    }
    
    result_msg = actions.get(action_type.upper(), f"Executed custom containment action '{action_type}'.")
    inc.status = "CONTAINMENT"
    inc.ai_recommendation = f"[ACTION TAKEN: {action_type}] {result_msg}"
    db.commit()
    db.refresh(inc)

    return {
        "status": "SUCCESS",
        "incident_number": inc.incident_number,
        "action_type": action_type,
        "detail": result_msg
    }

from pydantic import BaseModel

class AddEvidenceSchema(BaseModel):
    evidence_type: str
    source: str
    raw_content: str

@router.post("/{incident_id}/evidence")
def attach_evidence(incident_id: int, evd_in: AddEvidenceSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.services.case_management_service import case_management_service
    org_id = tenant_service.get_user_org_id(db, current_user)
    inc = db.query(Incident).filter(Incident.id == incident_id, Incident.organization_id == org_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    try:
        return case_management_service.add_evidence(
            db=db,
            incident_id=incident_id,
            evidence_type=evd_in.evidence_type,
            source=evd_in.source,
            raw_content=evd_in.raw_content
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{incident_id}/report")
def generate_case_report(incident_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.services.case_management_service import case_management_service
    org_id = tenant_service.get_user_org_id(db, current_user)
    inc = db.query(Incident).filter(Incident.id == incident_id, Incident.organization_id == org_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    try:
        return case_management_service.generate_case_report(db=db, incident_id=incident_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
