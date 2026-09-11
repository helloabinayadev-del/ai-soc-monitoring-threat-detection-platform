from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogResponse
from app.core.rbac import require_roles

router = APIRouter()

@router.get("/", response_model=List[AuditLogResponse])
def get_audit_logs(
    skip: int = 0,
    limit: int = 50,
    actor: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["Admin", "Analyst", "Auditor"]))
):
    query = db.query(AuditLog)
    if actor and actor != "ALL":
        query = query.filter(AuditLog.actor_username == actor)
    if action and action != "ALL":
        query = query.filter(AuditLog.action == action)
    if resource_type and resource_type != "ALL":
        query = query.filter(AuditLog.resource_type == resource_type)
    if status and status != "ALL":
        query = query.filter(AuditLog.status == status)

    return query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
