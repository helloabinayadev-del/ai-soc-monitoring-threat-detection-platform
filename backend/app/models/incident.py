from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from datetime import datetime, timezone
from app.core.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_number = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    severity = Column(String, default="HIGH", index=True) # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String, default="OPEN", index=True) # OPEN, CONTAINMENT, REMEDIATION, CLOSED
    assignee = Column(String, nullable=True)
    affected_systems = Column(JSON, nullable=True) # List of hostnames/IPs
    mitre_tactics = Column(JSON, nullable=True) # List of MITRE tactics
    ai_recommendation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    correlation_id = Column(String, index=True, nullable=True)
    alert_ids = Column(JSON, nullable=True) # List of linked SecurityAlert IDs
    timeline = Column(JSON, nullable=True) # Audit trail: [{"time": "...", "action": "..."}]
    notes = Column(JSON, nullable=True) # Analyst notes: [{"author": "...", "text": "...", "timestamp": "..."}]
    organization_id = Column(Integer, default=1, index=True)


