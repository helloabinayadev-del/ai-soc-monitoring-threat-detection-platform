from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class OrganizationCreate(BaseModel):
    name: str
    slug: str

class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MemberCreate(BaseModel):
    user_id: int
    role: str = "Analyst"

class MemberResponse(BaseModel):
    id: int
    organization_id: int
    user_id: int
    role: str
    joined_at: Optional[datetime] = None

    class Config:
        from_attributes = True
