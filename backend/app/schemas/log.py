from pydantic import BaseModel, ConfigDict, field_serializer
from typing import Optional, Dict, Any
from datetime import datetime, timezone

class LogEventBase(BaseModel):
    log_source: str
    event_type: str
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    user_name: Optional[str] = None
    hostname: Optional[str] = None
    action: Optional[str] = None
    severity: str = "INFORMATIONAL"
    raw_message: str
    parsed_fields: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None

class LogEventCreate(LogEventBase):
    pass

class LogEventResponse(LogEventBase):
    id: int
    timestamp: datetime
    anomaly_score: float = 0.0
    is_anomaly: str = "NORMAL"

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('timestamp')
    def serialize_timestamp(self, dt: datetime, _info) -> str:
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat().replace('+00:00', 'Z')
