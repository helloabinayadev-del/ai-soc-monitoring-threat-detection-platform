from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.ai.threat_classifier import threat_classifier
from app.models.alert import SecurityAlert

class AttackMappingService:
    def __init__(self):
        self.attack_version = "MITRE ATT&CK v14.1 (Enterprise)"
        self.tactics = [
            {"id": "TA0043", "name": "Reconnaissance"},
            {"id": "TA0042", "name": "Resource Development"},
            {"id": "TA0001", "name": "Initial Access"},
            {"id": "TA0002", "name": "Execution"},
            {"id": "TA0003", "name": "Persistence"},
            {"id": "TA0004", "name": "Privilege Escalation"},
            {"id": "TA0005", "name": "Defense Evasion"},
            {"id": "TA0006", "name": "Credential Access"},
            {"id": "TA0007", "name": "Discovery"},
            {"id": "TA0008", "name": "Lateral Movement"},
            {"id": "TA0009", "name": "Collection"},
            {"id": "TA0011", "name": "Command and Control"},
            {"id": "TA0010", "name": "Exfiltration"},
            {"id": "TA0040", "name": "Impact"}
        ]

    def get_coverage_matrix(self) -> Dict[str, Any]:
        """Calculates detection rule coverage across 14 MITRE ATT&CK tactics."""
        active_rules = [r for r in threat_classifier.rules if r.get("status") == "ACTIVE"]
        covered_tactics = {}

        for rule in active_rules:
            tactic_raw = rule.get("tactic", "")
            technique_raw = rule.get("technique", "")
            for tac in self.tactics:
                if tac["id"] in tactic_raw or tac["name"].lower() in tactic_raw.lower():
                    if tac["name"] not in covered_tactics:
                        covered_tactics[tac["name"]] = []
                    covered_tactics[tac["name"]].append({
                        "rule_id": rule["id"],
                        "rule_name": rule["name"],
                        "technique": technique_raw,
                        "status": "DETECTED"
                    })

        matrix = []
        covered_count = 0

        for tac in self.tactics:
            tac_name = tac["name"]
            rules_list = covered_tactics.get(tac_name, [])
            coverage_status = "DETECTED" if len(rules_list) > 0 else "NOT_COVERED"
            if len(rules_list) > 0:
                covered_count += 1
            matrix.append({
                "tactic_id": tac["id"],
                "tactic_name": tac_name,
                "coverage_status": coverage_status,
                "rules_count": len(rules_list),
                "mapped_rules": rules_list
            })

        coverage_pct = round((covered_count / len(self.tactics)) * 100, 1)

        return {
            "attack_version": self.attack_version,
            "total_tactics": len(self.tactics),
            "covered_tactics_count": covered_count,
            "coverage_percentage": coverage_pct,
            "coverage_matrix": matrix
        }

    def analyze_attack_chain(self, db: Session, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Builds evidence-grounded attack progression chain from actual correlated alerts.
        """
        query = db.query(SecurityAlert)
        if correlation_id:
            query = query.filter(SecurityAlert.correlation_id == correlation_id)
        alerts = query.order_by(SecurityAlert.created_at.asc()).all()

        observed_stages = []
        tactics_order = ["Initial Access", "Execution", "Privilege Escalation", "Credential Access", "Command and Control", "Exfiltration"]

        seen_tactics = set()
        for alt in alerts:
            tac = getattr(alt, "mitre_tactic", getattr(alt, "category", "Unknown"))
            tech = getattr(alt, "mitre_technique", "Unknown")
            seen_tactics.add(str(tac))
            observed_stages.append({
                "alert_id": alt.id,
                "alert_title": alt.title,
                "tactic": tac,
                "technique": tech,
                "confidence": "HIGH_CONFIDENCE" if alt.detection_source == "HYBRID" else "POSSIBLE",
                "evidence": f"Log event triggered rule '{alt.rule_id}' with risk score {alt.risk_score}",
                "timestamp": alt.created_at.isoformat() if alt.created_at else None
            })

        progression_chain = []
        for tac_name in tactics_order:
            is_observed = any(tac_name.lower() in str(stage["tactic"]).lower() for stage in observed_stages)
            progression_chain.append({
                "tactic_name": tac_name,
                "status": "OBSERVED" if is_observed else "MISSING_EVIDENCE",
                "confidence": "HIGH_CONFIDENCE" if is_observed else "NOT_ESTABLISHED"
            })

        is_complete = sum(1 for p in progression_chain if p["status"] == "OBSERVED") >= 3

        return {
            "attack_version": self.attack_version,
            "correlation_id": correlation_id or "GLOBAL_TELEMETRY",
            "chain_classification": "FULL_ATTACK_CHAIN" if is_complete else "PARTIAL_ATTACK_CHAIN",
            "total_observed_stages": len(observed_stages),
            "observed_stages": observed_stages,
            "tactical_progression": progression_chain
        }

attack_mapping_service = AttackMappingService()
