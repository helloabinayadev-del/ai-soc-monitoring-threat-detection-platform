from pydantic import BaseModel, ConfigDict, field_serializer
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

class AlertBase(BaseModel):
    title: str
    description: str
    rule_id: str
    severity: str = "MEDIUM"
    category: str
    mitre_tactic: Optional[str] = None
    mitre_technique: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    affected_asset: Optional[str] = None
    risk_score: float = 50.0
    priority: Optional[str] = "MEDIUM"
    detection_source: Optional[str] = "RULE_BASED"
    risk_factors: Optional[List[Dict[str, Any]]] = None
    anomaly_score: Optional[float] = 0.0
    status: str = "NEW"
    raw_payload: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None
    source_event_ids: Optional[List[int]] = None

class AlertCreate(AlertBase):
    pass

class AlertUpdateStatus(BaseModel):
    status: str

class AlertResponse(AlertBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime, _info) -> str:
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat().replace('+00:00', 'Z')
