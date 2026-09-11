from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
from app.models.audit_log import AuditLog

class AuditService:
    @staticmethod
    def record_action(
        db: Session,
        actor_username: str,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        status: str = "SUCCESS",
        ip_address: Optional[str] = None,
        details: Optional[str] = None
    ) -> AuditLog:
        audit_entry = AuditLog(
            timestamp=datetime.now(timezone.utc),
            actor_username=actor_username,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            status=status,
            ip_address=ip_address,
            details=details
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        return audit_entry

audit_service = AuditService()
