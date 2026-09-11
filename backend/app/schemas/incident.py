from pydantic import BaseModel, ConfigDict, field_serializer
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

class IncidentBase(BaseModel):
    title: str
    summary: str
    severity: str = "HIGH"
    status: str = "OPEN"
    assignee: Optional[str] = None
    affected_systems: Optional[List[str]] = None
    mitre_tactics: Optional[List[str]] = None
    ai_recommendation: Optional[str] = None
    correlation_id: Optional[str] = None
    alert_ids: Optional[List[int]] = None
    timeline: Optional[List[Dict[str, Any]]] = None
    notes: Optional[List[Dict[str, Any]]] = None

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    assignee: Optional[str] = None
    ai_recommendation: Optional[str] = None
    notes: Optional[List[Dict[str, Any]]] = None

class IncidentResponse(IncidentBase):
    id: int
    incident_number: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime, _info) -> str:
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat().replace('+00:00', 'Z')
