from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON
from datetime import datetime, timezone
from app.core.database import Base

class LogEvent(Base):
    __tablename__ = "log_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    log_source = Column(String, index=True) # Firewall, WindowsEvent, LinuxSyslog, AWSCloudTrail, EndpointEDR
    event_type = Column(String, index=True) # Authentication, NetworkConnection, ProcessCreation, PrivilegeEscalation
    source_ip = Column(String, index=True, nullable=True)
    destination_ip = Column(String, index=True, nullable=True)
    source_port = Column(Integer, nullable=True)
    destination_port = Column(Integer, nullable=True)
    user_name = Column(String, index=True, nullable=True)
    hostname = Column(String, index=True, nullable=True)
    action = Column(String, nullable=True) # ALLOW, DENY, EXECUTE, FAIL, SUCCESS
    severity = Column(String, default="INFORMATIONAL") # INFORMATIONAL, LOW, MEDIUM, HIGH, CRITICAL
    raw_message = Column(Text, nullable=False)
    parsed_fields = Column(JSON, nullable=True)
    anomaly_score = Column(Float, default=0.0)
    is_anomaly = Column(String, default="NORMAL") # NORMAL, ANOMALOUS
    model_version = Column(String, default="IsolationForest-v1", nullable=True)
    feature_vector = Column(JSON, nullable=True)
    correlation_id = Column(String, index=True, nullable=True)
    organization_id = Column(Integer, default=1, index=True)

