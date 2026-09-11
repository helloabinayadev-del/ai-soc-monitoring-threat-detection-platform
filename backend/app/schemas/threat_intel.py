from pydantic import BaseModel, ConfigDict, field_serializer
from typing import Optional
from datetime import datetime, timezone

class ThreatIntelBase(BaseModel):
    ioc_value: str
    ioc_type: str
    threat_type: Optional[str] = None
    threat_score: float = 75.0
    source_feed: Optional[str] = "AlienVault OTX / Custom Feed"
    description: Optional[str] = None

class ThreatIntelCreate(ThreatIntelBase):
    pass

class ThreatIntelResponse(ThreatIntelBase):
    id: int
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('last_updated')
    def serialize_last_updated(self, dt: datetime, _info) -> str:
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat().replace('+00:00', 'Z')
