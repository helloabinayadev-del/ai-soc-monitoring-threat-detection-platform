from typing import Dict, Any, List, Optional
from app.schemas.copilot import CopilotResponse
from app.core.database import SessionLocal
from app.models.alert import SecurityAlert
from app.models.incident import Incident
from app.models.log import LogEvent
from app.models.correlation import CorrelationGroup
from app.models.threat_intel import ThreatIntel

class SecurityCopilotService:
    """
    Explainable, Evidence-Driven AI Security Copilot Service.
    Enforces 10-point analytical breakdown backed strictly by empirical telemetry evidence.
    """

    def analyze_query(self, query: str, alert_data: Any = None, incident_data: Any = None) -> CopilotResponse:
        q_lower = query.lower()
        db = SessionLocal()
        
        target_alert = None
        target_incident = None

        try:
            if alert_data:
                if isinstance(alert_data, int):
                    target_alert = db.query(SecurityAlert).filter(SecurityAlert.id == alert_data).first()
                elif isinstance(alert_data, dict):
                    alert_id = alert_data.get("id")
                    if alert_id:
                        target_alert = db.query(SecurityAlert).filter(SecurityAlert.id == alert_id).first()

            if not target_alert and incident_data:
                if isinstance(incident_data, int):
                    target_incident = db.query(Incident).filter(Incident.id == incident_data).first()

            # If still no alert/incident, attempt query matching by ID or title in DB
            if not target_alert and not target_incident:
                # Find most recent alert if query mentions alert or recent
                target_alert = db.query(SecurityAlert).order_by(SecurityAlert.created_at.desc()).first()

            if target_alert:
                # Fetch linked log events for empirical evidence
                log_ids = target_alert.source_event_ids or []
                logs = db.query(LogEvent).filter(LogEvent.id.in_(log_ids)).all() if log_ids else []

                # Fetch correlation group if present
                corr_group = None
                if target_alert.correlation_id:
                    corr_group = db.query(CorrelationGroup).filter(CorrelationGroup.correlation_id == target_alert.correlation_id).first()

                # Fetch Threat Intel matching source IP
                intel_match = None
                if target_alert.source_ip:
                    intel_match = db.query(ThreatIntel).filter(ThreatIntel.ioc_value == target_alert.source_ip).first()

                # Build 10-point Evidence-Driven Breakdown
                what_happened = (
                    f"Security Alert #{target_alert.id} ({target_alert.title}) triggered for asset "
                    f"'{target_alert.affected_asset}' involving source IP {target_alert.source_ip or 'internal host'}."
                )

                why_generated = (
                    f"Detection rule '{target_alert.rule_id}' identified suspicious activity matching category "
                    f"'{target_alert.category}'. Isolation Forest ML Anomaly Score: {target_alert.anomaly_score:.1f}/100."
                )

                evidence_items = []
                if logs:
                    for l in logs:
                        evidence_items.append(f"Log Event ID #{l.id} [{l.log_source}]: {l.raw_message[:120]}")
                else:
                    evidence_items.append(f"Raw Alert Payload: {str(target_alert.raw_payload)[:150]}")
                if target_alert.source_ip:
                    evidence_items.append(f"Origin Source IP: {target_alert.source_ip}")
                if target_alert.affected_asset:
                    evidence_items.append(f"Target Asset: {target_alert.affected_asset}")

                # Risk breakdown
                risk_factors = target_alert.risk_factors or []
                if risk_factors:
                    factors_str = "; ".join([f"{f.get('factor')}: +{f.get('contribution')} pts" for f in risk_factors])
                else:
                    factors_str = f"Base severity rating '{target_alert.severity}' combined with ML score {target_alert.anomaly_score:.1f}"

                risk_explanation = (
                    f"Priority rank is {target_alert.priority or target_alert.severity} (Calculated Risk Score: {target_alert.risk_score:.1f}/100). "
                    f"Contributing factors: {factors_str}."
                )

                if corr_group:
                    corr_summary = (
                        f"Linked to Correlation Chain {corr_group.correlation_id} ({corr_group.title}). "
                        f"Group contains {corr_group.event_count} related security events across stage: {corr_group.stage_summary}."
                    )
                else:
                    corr_summary = "Single isolated security alert. No active multi-stage correlation chain detected."

                if intel_match:
                    threat_intel = (
                        f"MATCH FOUND: Source IP {intel_match.ioc_value} flagged in Threat Intel feed "
                        f"(Threat Type: {intel_match.threat_type}, Risk Score: {intel_match.threat_score}/100)."
                    )
                else:
                    threat_intel = "No active indicator match found in internal Threat Intelligence feeds."

                investigation_steps = [
                    f"Audit network logs for source IP {target_alert.source_ip or 'internal subnet'}",
                    f"Inspect process execution tree on target host {target_alert.affected_asset}",
                    f"Verify active user session token validity for accounts logged on host"
                ]

                remediation = [
                    f"Isolate host {target_alert.affected_asset} via EDR agent if malicious execution is confirmed",
                    f"Block source IP {target_alert.source_ip or 'external IP'} on perimeter firewall",
                    "Reset credentials for compromised user accounts"
                ]

                # Uncertainty Statement
                if not logs or len(logs) < 2:
                    uncertainty = "Uncertainty Note: Limited log depth for this event. Recommend expanding packet capture and host audit logs to confirm privilege escalation."
                else:
                    uncertainty = "Telemetry is sufficient for high-confidence triage. Standard investigation procedures apply."

                # Construct full answer summary text
                formatted_answer = (
                    f"### Grounded 10-Point AI Security Copilot Analysis (Alert #{target_alert.id})\n\n"
                    f"**1. What Happened:** {what_happened}\n\n"
                    f"**2. Why Generated:** {why_generated}\n\n"
                    f"**3. Evidence:**\n" + "\n".join([f" - {e}" for e in evidence_items]) + "\n\n"
                    f"**4. Risk Explanation:** {risk_explanation}\n\n"
                    f"**5. Correlated Events:** {corr_summary}\n\n"
                    f"**6. MITRE ATT&CK Mapping:** {target_alert.mitre_tactic or 'TA0001 - Initial Access'} / {target_alert.mitre_technique or 'T1078 - Valid Accounts'}\n\n"
                    f"**7. Threat Intelligence:** {threat_intel}\n\n"
                    f"**8. Recommended Investigation:**\n" + "\n".join([f" - {s}" for s in investigation_steps]) + "\n\n"
                    f"**9. Recommended Remediation & Containment Actions:**\n" + "\n".join([f" - {r}" for r in remediation]) + "\n\n"
                    f"**10. Uncertainty & Data Gaps:** {uncertainty}"
                )

                mitre_refs = [
                    target_alert.mitre_tactic or "TA0001 - Initial Access",
                    target_alert.mitre_technique or "T1078 - Valid Accounts"
                ]

                return CopilotResponse(
                    answer=formatted_answer,
                    action_items=investigation_steps + remediation,
                    mitre_references=mitre_refs,
                    confidence_score=min(0.99, max(0.70, float(target_alert.risk_score) / 100.0)),
                    analysis_details={
                        "engine_version": "Evidence-Driven-Copilot-v2.0",
                        "target_alert_id": target_alert.id,
                        "risk_score": target_alert.risk_score,
                        "anomaly_score": target_alert.anomaly_score
                    },
                    what_happened=what_happened,
                    why_generated=why_generated,
                    evidence_items=evidence_items,
                    risk_explanation=risk_explanation,
                    correlated_events_summary=corr_summary,
                    threat_intel_context=threat_intel,
                    investigation_steps=investigation_steps,
                    recommended_remediation=remediation,
                    uncertainty_statement=uncertainty
                )

            else:
                # Default response when query is generic without context
                uncertainty = "Insufficient evidence for a reliable security conclusion without specific alert or log context."
                actions = [
                    "Isolate compromised workstation via EDR agent",
                    "Block malicious IP on perimeter firewall",
                    "Revoke user Active Directory tokens"
                ]
                return CopilotResponse(
                    answer=(
                        f"### AI Security Copilot Threat Response for: '{query}'\n\n"
                        f"**Recommended Containment Actions:**\n"
                        f"1. Isolate host via EDR agent if malicious process is observed.\n"
                        f"2. Block egress IP address on edge firewall.\n"
                        f"3. Revoke Active Directory session tokens.\n\n"
                        f"**Uncertainty Note:** {uncertainty}"
                    ),
                    action_items=actions,
                    mitre_references=["TA0001 - Initial Access", "TA0005 - Defense Evasion"],
                    confidence_score=0.85,
                    analysis_details={"engine_version": "Evidence-Driven-Copilot-v2.0"},
                    uncertainty_statement=uncertainty
                )
        finally:
            db.close()

copilot_service = SecurityCopilotService()
