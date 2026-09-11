from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.correlation import CorrelationGroup
from app.models.log import LogEvent
from app.models.alert import SecurityAlert

router = APIRouter()

@router.get("/")
def list_correlation_groups(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(CorrelationGroup)
    if status and status != "ALL":
        query = query.filter(CorrelationGroup.status == status)
    groups = query.order_by(CorrelationGroup.last_seen.desc()).offset(skip).limit(limit).all()
    return groups

@router.get("/{correlation_id}")
def get_correlation_detail(correlation_id: str, db: Session = Depends(get_db)):
    group = db.query(CorrelationGroup).filter(CorrelationGroup.correlation_id == correlation_id).first()
    if not group:
        raise HTTPException(status_code=404, detail=f"Correlation group '{correlation_id}' not found")
    
    events = db.query(LogEvent).filter(LogEvent.id.in_(group.event_ids or [])).all() if group.event_ids else []
    alerts = db.query(SecurityAlert).filter(SecurityAlert.id.in_(group.alert_ids or [])).all() if group.alert_ids else []

    return {
        "correlation_group": group,
        "related_events": events,
        "related_alerts": alerts
    }
