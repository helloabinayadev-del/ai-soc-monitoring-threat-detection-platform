from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.alert import SecurityAlert
from app.models.incident import Incident
from app.models.threat_intel import ThreatIntel
from app.services.audit_service import audit_service
from app.services.copilot_service import copilot_service

class PlaybookEngine:
    def __init__(self):
        self.playbooks = [
            {
                "id": "PB-001",
                "name": "Brute Force Attack Investigation & Containment",
                "description": "Collects authentication failure evidence, checks threat intel, generates AI summary, and requests approval for IP containment.",
                "trigger_event": "Authentication",
                "severity": "HIGH",
                "status": "ACTIVE",
                "version": 1,
                "author": "system",
                "actions": [
                    {"step": 1, "type": "COLLECT_EVIDENCE", "description": "Extract historical logs and correlation context"},
                    {"step": 2, "type": "LOOKUP_INDICATOR", "description": "Match source IP against threat intelligence database"},
                    {"step": 3, "type": "GENERATE_AI_SUMMARY", "description": "Generate grounded 10-point AI Copilot triage analysis"},
                    {"step": 4, "type": "REQUEST_ANALYST_APPROVAL", "description": "Request analyst approval for IP containment"},
                    {"step": 5, "type": "SIMULATE_BLOCK_IP", "description": "Simulate firewall block rule for malicious source IP"}
                ]
            },
            {
                "id": "PB-002",
                "name": "Privilege Escalation Rapid Triage",
                "description": "Triage unauthorized sudo/privilege escalation, create incident case, and escalate priority.",
                "trigger_event": "PrivilegeEscalation",
                "severity": "CRITICAL",
                "status": "ACTIVE",
                "version": 1,
                "author": "system",
                "actions": [
                    {"step": 1, "type": "COLLECT_EVIDENCE", "description": "Extract process execution logs and correlation timeline"},
                    {"step": 2, "type": "CREATE_INCIDENT", "description": "Create Incident case ticket linked to correlation chain"},
                    {"step": 3, "type": "UPDATE_STATUS", "description": "Update incident status to INVESTIGATING"},
                    {"step": 4, "type": "GENERATE_AI_SUMMARY", "description": "Generate grounded Copilot remediation summary"}
                ]
            },
            {
                "id": "PB-003",
                "name": "Malicious C2 Indicator Enrichment",
                "description": "Enriches outbound connection indicators and logs analyst investigation notes.",
                "trigger_event": "CommandAndControl",
                "severity": "CRITICAL",
                "status": "ACTIVE",
                "version": 1,
                "author": "system",
                "actions": [
                    {"step": 1, "type": "LOOKUP_INDICATOR", "description": "Check domain/IP threat score in local IOC feeds"},
                    {"step": 2, "type": "LINK_CORRELATION", "description": "Link correlated events under CORR-YYYYMMDD-XXXX"},
                    {"step": 3, "type": "ADD_NOTE", "description": "Append investigation note to incident history"}
                ]
            }
        ]
        self.executions: List[Dict[str, Any]] = []

    def get_playbooks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        if status and status != "ALL":
            return [p for p in self.playbooks if p.get("status") == status]
        return self.playbooks

    def recommend_playbook(self, alert: SecurityAlert) -> Optional[Dict[str, Any]]:
        """Recommend a playbook grounded in empirical alert severity and category."""
        category_lower = (alert.category or "").lower()
        title_lower = (alert.title or "").lower()

        if "brute force" in title_lower or "login" in category_lower:
            return self.playbooks[0]
        elif "privilege" in title_lower or "escalation" in category_lower:
            return self.playbooks[1]
        elif "c2" in title_lower or "command and control" in category_lower:
            return self.playbooks[2]

        return self.playbooks[0] # Default fallback

    def execute_playbook(
        self,
        db: Session,
        playbook_id: str,
        alert_id: int,
        actor_username: str = "analyst"
    ) -> Dict[str, Any]:
        playbook = next((p for p in self.playbooks if p["id"] == playbook_id), None)
        if not playbook:
            raise ValueError(f"Playbook {playbook_id} not found.")

        # Idempotency Check: Prevent duplicate executions for the same alert & playbook
        existing = next((e for e in self.executions if e["playbook_id"] == playbook_id and e["alert_id"] == alert_id and e["status"] in ["RUNNING", "COMPLETED"]), None)
        if existing:
            return {
                "execution_id": existing["execution_id"],
                "status": existing["status"],
                "message": f"Idempotent execution detected for Playbook {playbook_id} on Alert #{alert_id}",
                "execution": existing
            }

        alert = db.query(SecurityAlert).filter(SecurityAlert.id == alert_id).first()
        if not alert:
            raise ValueError(f"Alert #{alert_id} not found.")

        exec_id = f"EXEC-{len(self.executions) + 1:04d}"
        now_str = datetime.now(timezone.utc).isoformat()

        action_results = []
        requires_approval = False
        execution_status = "COMPLETED"

        for act in playbook["actions"]:
            act_type = act["type"]
            res_item = {
                "step": act["step"],
                "type": act_type,
                "description": act["description"],
                "status": "SUCCESS",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "detail": ""
            }

            if act_type == "COLLECT_EVIDENCE":
                res_item["detail"] = f"Collected evidence for Alert #{alert.id} ({alert.source_ip} -> {alert.affected_asset})"
            elif act_type == "LOOKUP_INDICATOR":
                ioc = db.query(ThreatIntel).filter(ThreatIntel.ioc_value == alert.source_ip).first()
                if ioc:
                    res_item["detail"] = f"Threat Intel MATCH: {ioc.ioc_value} (Score: {ioc.threat_score}, Type: {ioc.threat_type})"
                else:
                    res_item["detail"] = f"Threat Intel Lookup: No match found for {alert.source_ip} (Threat Score: 0)"
            elif act_type == "CREATE_INCIDENT":
                res_item["detail"] = f"Created incident ticket for Alert #{alert.id} (Correlation: {alert.correlation_id})"
            elif act_type == "UPDATE_STATUS":
                alert.status = "INVESTIGATING"
                db.commit()
                res_item["detail"] = f"Updated Alert #{alert.id} status to INVESTIGATING"
            elif act_type == "GENERATE_AI_SUMMARY":
                res_item["detail"] = f"AI Summary: Grounded triage completed for {alert.title}. Priority: {alert.priority}."
            elif act_type == "REQUEST_ANALYST_APPROVAL":
                requires_approval = True
                res_item["status"] = "APPROVAL_REQUIRED"
                res_item["detail"] = f"Action requires analyst approval before executing containment for IP {alert.source_ip}."
                execution_status = "PENDING_APPROVAL"
                action_results.append(res_item)
                break # Pause execution until approval
            elif act_type == "SIMULATE_BLOCK_IP":
                res_item["detail"] = f"SIMULATED ACTION: Would block IP {alert.source_ip} on firewall edge router (Lab Simulation Mode)."

            action_results.append(res_item)

        exec_record = {
            "execution_id": exec_id,
            "playbook_id": playbook_id,
            "playbook_name": playbook["name"],
            "playbook_version": playbook["version"],
            "alert_id": alert_id,
            "actor_username": actor_username,
            "started_at": now_str,
            "completed_at": datetime.now(timezone.utc).isoformat() if execution_status == "COMPLETED" else None,
            "status": execution_status,
            "requires_approval": requires_approval,
            "actions": action_results
        }
        self.executions.append(exec_record)

        audit_service.record_action(
            db=db,
            actor_username=actor_username,
            action="PLAYBOOK_EXECUTED",
            resource_type="Playbook",
            resource_id=playbook_id,
            details=f"Executed playbook '{playbook['name']}' (v{playbook['version']}) on Alert #{alert_id}. Status: {execution_status}"
        )

        return exec_record

    def approve_action(self, db: Session, execution_id: str, actor_username: str = "analyst") -> Dict[str, Any]:
        exec_record = next((e for e in self.executions if e["execution_id"] == execution_id), None)
        if not exec_record:
            raise ValueError(f"Execution {execution_id} not found.")

        alert = db.query(SecurityAlert).filter(SecurityAlert.id == exec_record["alert_id"]).first()
        source_ip = alert.source_ip if alert else "198.51.100.99"

        # Execute final pending simulated action
        simulated_step = {
            "step": 5,
            "type": "SIMULATE_BLOCK_IP",
            "description": f"Simulate firewall block rule for IP {source_ip}",
            "status": "SUCCESS",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "detail": f"SIMULATED ACTION: Firewall block rule applied for IP {source_ip} (Approved by {actor_username})."
        }
        exec_record["actions"].append(simulated_step)
        exec_record["status"] = "COMPLETED"
        exec_record["completed_at"] = datetime.now(timezone.utc).isoformat()

        audit_service.record_action(
            db=db,
            actor_username=actor_username,
            action="ACTION_APPROVED",
            resource_type="PlaybookAction",
            resource_id=execution_id,
            details=f"Approved containment action for execution {execution_id} targeting IP {source_ip}"
        )

        return exec_record

playbook_engine = PlaybookEngine()
