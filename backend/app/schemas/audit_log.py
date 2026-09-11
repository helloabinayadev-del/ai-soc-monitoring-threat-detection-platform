from pydantic import BaseModel, ConfigDict, field_serializer
from typing import Optional
from datetime import datetime, timezone

class AuditLogBase(BaseModel):
    actor_username: str
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    status: str = "SUCCESS"
    ip_address: Optional[str] = None
    details: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogResponse(AuditLogBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('timestamp')
    def serialize_timestamp(self, dt: datetime, _info) -> str:
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat().replace('+00:00', 'Z')
