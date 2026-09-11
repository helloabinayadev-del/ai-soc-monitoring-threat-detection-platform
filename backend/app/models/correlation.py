from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from datetime import datetime, timezone
from app.core.database import Base

class CorrelationGroup(Base):
    __tablename__ = "correlation_groups"

    id = Column(Integer, primary_key=True, index=True)
    correlation_id = Column(String, unique=True, index=True, nullable=False) # e.g. CORR-2026-0001
    title = Column(String, nullable=False, default="Potential Multi-Stage Attack Pattern")
    stage_summary = Column(String, nullable=True) # e.g. "Credential Access -> Execution -> Privilege Escalation"
    source_ip = Column(String, index=True, nullable=True)
    target_asset = Column(String, index=True, nullable=True)
    event_ids = Column(JSON, nullable=False) # List of LogEvent IDs
    alert_ids = Column(JSON, nullable=False) # List of SecurityAlert IDs
    event_count = Column(Integer, default=1)
    risk_score = Column(Float, default=50.0)
    priority = Column(String, default="MEDIUM", index=True) # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String, default="ACTIVE", index=True) # ACTIVE, INVESTIGATING, RESOLVED
    first_seen = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    mitre_tactics = Column(JSON, nullable=True) # List of tactics mapped
    organization_id = Column(Integer, default=1, index=True)

