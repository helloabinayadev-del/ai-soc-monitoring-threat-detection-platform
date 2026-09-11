from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.alert import SecurityAlert
from app.schemas.alert import AlertResponse, AlertCreate, AlertUpdateStatus

router = APIRouter()

@router.get("/", response_model=List[AlertResponse])
def get_alerts(
    skip: int = 0,
    limit: int = 50,
    severity: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    detection_source: Optional[str] = None,
    min_risk_score: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(SecurityAlert)
    if severity and severity != "ALL":
        query = query.filter(SecurityAlert.severity == severity)
    if priority and priority != "ALL":
        query = query.filter(SecurityAlert.priority == priority)
    if status and status != "ALL":
        query = query.filter(SecurityAlert.status == status)
    if detection_source and detection_source != "ALL":
        query = query.filter(SecurityAlert.detection_source == detection_source)
    if min_risk_score is not None:
        query = query.filter(SecurityAlert.risk_score >= min_risk_score)

    return query.order_by(SecurityAlert.risk_score.desc(), SecurityAlert.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(SecurityAlert).filter(SecurityAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert #{alert_id} not found")
    return alert

@router.patch("/{alert_id}/status", response_model=AlertResponse)
def update_alert_status(alert_id: int, status_update: AlertUpdateStatus, db: Session = Depends(get_db)):
    alert = db.query(SecurityAlert).filter(SecurityAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert #{alert_id} not found")
    alert.status = status_update.status
    db.commit()
    db.refresh(alert)
    return alert
