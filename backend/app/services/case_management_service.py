import hashlib
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.alert import SecurityAlert
from app.services.audit_service import audit_service

class CaseManagementService:
    def add_evidence(
        self,
        db: Session,
        incident_id: int,
        evidence_type: str,
        source: str,
        raw_content: str,
        actor_username: str = "analyst"
    ) -> Dict[str, Any]:
        """
        Attaches raw evidence with cryptographic SHA-256 hash integrity calculation.
        """
        inc = db.query(Incident).filter(Incident.id == incident_id).first()
        if not inc:
            raise ValueError(f"Incident / Case #{incident_id} not found.")

        content_bytes = raw_content.encode("utf-8")
        sha256_hash = hashlib.sha256(content_bytes).hexdigest()
        now_iso = datetime.now(timezone.utc).isoformat()
        evd_id = f"EVD-{hashlib.md5(content_bytes).hexdigest()[:8].upper()}"

        evidence_item = {
            "evidence_id": evd_id,
            "evidence_type": evidence_type,
            "source": source,
            "raw_content": raw_content,
            "sha256_hash": sha256_hash,
            "attached_by": actor_username,
            "attached_at": now_iso
        }

        current_timeline = list(inc.timeline or [])
        current_timeline.append({
            "timestamp": now_iso,
            "action": "EVIDENCE_ATTACHED",
            "actor": actor_username,
            "detail": f"Attached evidence {evd_id} ({evidence_type}) SHA-256: {sha256_hash[:16]}..."
        })

        inc.timeline = current_timeline
        db.commit()
        db.refresh(inc)

        audit_service.record_action(
            db=db,
            actor_username=actor_username,
            action="EVIDENCE_ATTACHED",
            resource_type="IncidentCase",
            resource_id=str(incident_id),
            details=f"Attached evidence {evd_id} with SHA-256 integrity hash {sha256_hash}"
        )

        return evidence_item

    def generate_case_report(self, db: Session, incident_id: int) -> Dict[str, Any]:
        """
        Generates structured case investigation report with cryptographic SHA-256 report hash.
        """
        inc = db.query(Incident).filter(Incident.id == incident_id).first()
        if not inc:
            raise ValueError(f"Incident / Case #{incident_id} not found.")

        alerts_data = []
        if inc.alert_ids:
            linked_alerts = db.query(SecurityAlert).filter(SecurityAlert.id.in_(inc.alert_ids)).all()
            for a in linked_alerts:
                alerts_data.append({
                    "alert_id": a.id,
                    "title": a.title,
                    "severity": a.severity,
                    "mitre_tactic": a.mitre_tactic,
                    "mitre_technique": a.mitre_technique
                })

        report_payload = {
            "report_title": f"Digital Forensics Case Investigation Report - {inc.incident_number}",
            "case_number": inc.incident_number,
            "status": inc.status,
            "severity": inc.severity,
            "assignee": inc.assignee or "Unassigned",
            "created_at": inc.created_at.isoformat() if inc.created_at else None,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": inc.summary,
            "linked_alerts": alerts_data,
            "timeline_events": inc.timeline or [],
            "analyst_notes": inc.notes or [],
            "ai_copilot_analysis": {
                "label": "AI-GENERATED CONTENT (GROUNDED RECOMMENDATIONS)",
                "content": inc.ai_recommendation or "No AI recommendations generated."
            }
        }

        # Calculate cryptographic SHA-256 hash of entire JSON report payload
        report_bytes = json.dumps(report_payload, sort_keys=True).encode("utf-8")
        report_hash = hashlib.sha256(report_bytes).hexdigest()
        report_payload["sha256_report_hash"] = report_hash

        return report_payload

case_management_service = CaseManagementService()
