from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.models.evaluation import AnalystFeedback
from app.models.alert import SecurityAlert
from app.services.audit_service import audit_service

router = APIRouter()

class FeedbackCreate(BaseModel):
    alert_id: Optional[int] = None
    incident_id: Optional[int] = None
    analyst_username: str = "analyst"
    feedback_type: str # TRUE_POSITIVE, FALSE_POSITIVE, RISK_TOO_HIGH, RISK_TOO_LOW
    comments: Optional[str] = None

@router.post("/")
def submit_analyst_feedback(fb_in: FeedbackCreate, db: Session = Depends(get_db)):
    feedback = AnalystFeedback(**fb_in.model_dump())
    db.add(feedback)
    
    # If feedback is for an Alert, update alert status/risk
    if fb_in.alert_id:
        alert = db.query(SecurityAlert).filter(SecurityAlert.id == fb_in.alert_id).first()
        if alert:
            if fb_in.feedback_type == "FALSE_POSITIVE":
                alert.status = "FALSE_POSITIVE"
                alert.risk_score = max(0.0, alert.risk_score - 30.0)
            elif fb_in.feedback_type == "TRUE_POSITIVE":
                alert.status = "INVESTIGATING"
                alert.risk_score = min(100.0, alert.risk_score + 10.0)
            db.commit()

    db.commit()
    db.refresh(feedback)

    audit_service.record_action(
        db=db,
        actor_username=fb_in.analyst_username,
        action="ANALYST_FEEDBACK_SUBMIT",
        resource_type="SecurityAlert" if fb_in.alert_id else "Incident",
        resource_id=fb_in.alert_id or fb_in.incident_id or 0,
        details=f"Analyst submitted feedback: {fb_in.feedback_type}"
    )

    return feedback
