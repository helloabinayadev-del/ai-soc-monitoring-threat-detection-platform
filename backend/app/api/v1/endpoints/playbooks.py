from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.services.playbook_engine import playbook_engine
from app.models.alert import SecurityAlert
from app.core.rbac import require_roles

router = APIRouter()

class PlaybookExecuteSchema(BaseModel):
    playbook_id: str
    alert_id: int

class PlaybookApproveSchema(BaseModel):
    execution_id: str

@router.get("/")
def list_playbooks(
    status: Optional[str] = None,
    current_user = Depends(require_roles(["Admin", "Analyst", "Auditor"]))
):
    return playbook_engine.get_playbooks(status=status)

@router.get("/recommend/{alert_id}")
def recommend_playbook_for_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["Admin", "Analyst"]))
):
    alert = db.query(SecurityAlert).filter(SecurityAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert #{alert_id} not found.")

    recommended = playbook_engine.recommend_playbook(alert)
    return {
        "alert_id": alert_id,
        "recommended_playbook": recommended
    }

@router.post("/execute")
def execute_playbook(
    exec_in: PlaybookExecuteSchema,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["Admin", "Analyst"]))
):
    try:
        actor = getattr(current_user, "username", "analyst")
        res = playbook_engine.execute_playbook(
            db=db,
            playbook_id=exec_in.playbook_id,
            alert_id=exec_in.alert_id,
            actor_username=actor
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/approve")
def approve_playbook_action(
    app_in: PlaybookApproveSchema,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["Admin", "Analyst"]))
):
    try:
        actor = getattr(current_user, "username", "analyst")
        res = playbook_engine.approve_action(
            db=db,
            execution_id=app_in.execution_id,
            actor_username=actor
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/executions")
def list_playbook_executions(
    current_user = Depends(require_roles(["Admin", "Analyst", "Auditor"]))
):
    return playbook_engine.executions
