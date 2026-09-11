from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.ai.threat_classifier import threat_classifier
from app.core.rbac import require_roles
from app.services.audit_service import audit_service

router = APIRouter()

class RuleCreateSchema(BaseModel):
    name: str = Field(..., min_length=3)
    description: Optional[str] = None
    category: str = "Custom Detection"
    tactic: Optional[str] = "TA0007 - Discovery"
    technique: Optional[str] = "T1082 - System Information Discovery"
    severity: str = "HIGH"
    priority: str = "HIGH"
    condition_field: str = "raw_message"
    condition_operator: str = "contains"
    condition_value: str = ""
    status: str = "ACTIVE"

class RuleTestSchema(BaseModel):
    rule: RuleCreateSchema
    test_log: Dict[str, Any]

@router.get("/")
def get_detection_rules(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    current_user = Depends(require_roles(["Admin", "Analyst", "Auditor"]))
):
    rules = threat_classifier.rules
    if status and status != "ALL":
        rules = [r for r in rules if r.get("status") == status]
    if severity and severity != "ALL":
        rules = [r for r in rules if r.get("severity") == severity]
    return rules

@router.post("/", response_model=Dict[str, Any])
def create_detection_rule(
    rule_in: RuleCreateSchema,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["Admin"]))
):
    rule_dict = rule_in.model_dump()
    validation = threat_classifier.validate_rule(rule_dict)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=f"Invalid rule: {', '.join(validation['errors'])}")

    author = getattr(current_user, "username", "admin")
    new_rule = threat_classifier.add_or_update_rule(rule_dict, author=author)

    audit_service.record_action(
        db=db,
        actor_username=author,
        action="RULE_CREATED",
        resource_type="DetectionRule",
        resource_id=new_rule["id"],
        details=f"Created detection rule '{new_rule['name']}' (v{new_rule['version']}) with severity {new_rule['severity']}"
    )

    return new_rule

@router.post("/test")
def test_detection_rule(
    test_in: RuleTestSchema,
    current_user = Depends(require_roles(["Admin", "Analyst"]))
):
    rule_dict = test_in.rule.model_dump()
    result = threat_classifier.test_rule(rule_dict, test_in.test_log)
    return result

@router.patch("/{rule_id}/status")
def update_rule_status(
    rule_id: str,
    status: str = Query(..., pattern="^(ACTIVE|DISABLED|DRAFT|DEPRECATED)$"),
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["Admin"]))
):
    rule = next((r for r in threat_classifier.rules if r["id"] == rule_id), None)
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found.")

    old_status = rule.get("status", "ACTIVE")
    rule["status"] = status
    author = getattr(current_user, "username", "admin")

    audit_service.record_action(
        db=db,
        actor_username=author,
        action="RULE_STATUS_CHANGE",
        resource_type="DetectionRule",
        resource_id=rule_id,
        details=f"Updated rule {rule_id} status: {old_status} -> {status}"
    )

    return {"message": f"Rule {rule_id} status updated to {status}", "rule": rule}
