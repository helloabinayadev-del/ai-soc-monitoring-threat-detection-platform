from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON
from datetime import datetime, timezone
from app.core.database import Base

class SecurityAlert(Base):
    __tablename__ = "security_alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    rule_id = Column(String, index=True, nullable=False)
    severity = Column(String, index=True, default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    category = Column(String, index=True) # Privilege Escalation, Command & Control, Data Exfiltration, Brute Force, Malware
    mitre_tactic = Column(String, nullable=True) # e.g. TA0004 - Privilege Escalation
    mitre_technique = Column(String, nullable=True) # e.g. T1078 - Valid Accounts
    source_ip = Column(String, nullable=True)
    destination_ip = Column(String, nullable=True)
    affected_asset = Column(String, nullable=True)
    risk_score = Column(Float, default=50.0)
    priority = Column(String, default="MEDIUM", index=True) # LOW, MEDIUM, HIGH, CRITICAL
    detection_source = Column(String, default="RULE_BASED", index=True) # RULE_BASED, ML_ANOMALY, HYBRID
    risk_factors = Column(JSON, nullable=True) # List of contributing factor breakdown dicts
    anomaly_score = Column(Float, default=0.0)
    status = Column(String, default="NEW", index=True) # NEW, INVESTIGATING, IN_PROGRESS, RESOLVED, FALSE_POSITIVE
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    raw_payload = Column(JSON, nullable=True)
    correlation_id = Column(String, index=True, nullable=True)
    source_event_ids = Column(JSON, nullable=True) # List of LogEvent IDs that triggered this alert
    organization_id = Column(Integer, default=1, index=True)


