from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from datetime import datetime, timezone
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    actor_username = Column(String, index=True, nullable=False)
    action = Column(String, index=True, nullable=False) # LOGIN, LOGOUT, LOG_INGEST, CONTAINMENT_ACTION, INCIDENT_CREATE, ROLE_UPDATE
    resource_type = Column(String, index=True, nullable=True) # User, LogEvent, SecurityAlert, Incident, ThreatIntel
    resource_id = Column(String, nullable=True)
    status = Column(String, default="SUCCESS") # SUCCESS, FAILED, DENIED
    ip_address = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    organization_id = Column(Integer, default=1, index=True)

