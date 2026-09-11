from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services.attack_mapping_service import attack_mapping_service

router = APIRouter()

@router.get("/coverage")
def get_mitre_coverage_matrix():
    return attack_mapping_service.get_coverage_matrix()

@router.get("/attack-chain")
def get_attack_chain(
    correlation_id: Optional[str] = Query(None, description="Optional correlation group ID"),
    db: Session = Depends(get_db)
):
    return attack_mapping_service.analyze_attack_chain(db=db, correlation_id=correlation_id)
