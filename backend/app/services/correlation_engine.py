from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.log import LogEvent
from app.models.alert import SecurityAlert
from app.models.correlation import CorrelationGroup

class EventCorrelationEngine:
    """
    Groups security events across time and entities (source IP, target host, user)
    into multi-stage attack chains with correlation IDs (e.g. CORR-20260827-0001).
    """

    CORRELATION_WINDOW_MINUTES = 30

    def correlate_event(self, db: Session, current_log: LogEvent, matched_rule: Optional[Dict[str, Any]] = None) -> CorrelationGroup:
        """
        Finds existing active correlation group matching entity (source IP / host / user)
        within 30 minutes, or creates a new correlation group.
        """
        now = current_log.timestamp or datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=self.CORRELATION_WINDOW_MINUTES)

        # Search for active correlation group matching source_ip, hostname, or user_name
        query = db.query(CorrelationGroup).filter(
            CorrelationGroup.status == "ACTIVE",
            CorrelationGroup.last_seen >= window_start
        )

        match_group = None
        if current_log.source_ip:
            match_group = query.filter(CorrelationGroup.source_ip == current_log.source_ip).first()

        if not match_group and current_log.hostname:
            match_group = query.filter(CorrelationGroup.target_asset == current_log.hostname).first()

        mitre_tactic = matched_rule.get("mitre_tactic") if matched_rule else None

        if match_group:
            # Update existing correlation group
            event_ids = list(match_group.event_ids or [])
            if current_log.id not in event_ids:
                event_ids.append(current_log.id)
            
            match_group.event_ids = event_ids
            match_group.event_count = len(event_ids)
            match_group.last_seen = now

            # Collect MITRE tactics
            tactics = list(match_group.mitre_tactics or [])
            if mitre_tactic and mitre_tactic not in tactics:
                tactics.append(mitre_tactic)
            match_group.mitre_tactics = tactics

            # Update stage summary
            if len(tactics) > 1:
                match_group.title = "Potential Multi-Stage Attack Pattern"
                match_group.stage_summary = " -> ".join(tactics)
                match_group.risk_score = min(100.0, match_group.risk_score + 15.0)
                match_group.priority = "HIGH" if match_group.risk_score < 85 else "CRITICAL"

            # Assign correlation_id to log event
            current_log.correlation_id = match_group.correlation_id
            db.commit()
            db.refresh(match_group)
            return match_group

        else:
            # Create new Correlation Group
            new_corr_id = f"CORR-{now.strftime('%Y%m%d')}-{db.query(CorrelationGroup).count() + 1:04d}"
            tactics = [mitre_tactic] if mitre_tactic else ["TA0007 - Discovery"]
            
            new_group = CorrelationGroup(
                correlation_id=new_corr_id,
                title="Potential Multi-Stage Attack Pattern" if matched_rule else "Correlated Security Activity Pattern",
                stage_summary=mitre_tactic or "Initial Telemetry Ingestion",
                source_ip=current_log.source_ip,
                target_asset=current_log.hostname or current_log.destination_ip or "Internal Workstation",
                event_ids=[current_log.id],
                alert_ids=[],
                event_count=1,
                risk_score=current_log.anomaly_score if current_log.anomaly_score > 50 else 50.0,
                priority="MEDIUM" if current_log.anomaly_score < 75 else "HIGH",
                status="ACTIVE",
                first_seen=now,
                last_seen=now,
                mitre_tactics=tactics
            )
            db.add(new_group)
            db.commit()
            db.refresh(new_group)

            current_log.correlation_id = new_corr_id
            db.commit()
            return new_group

    def link_alert_to_correlation(self, db: Session, correlation_id: str, alert_id: int):
        group = db.query(CorrelationGroup).filter(CorrelationGroup.correlation_id == correlation_id).first()
        if group:
            alert_ids = list(group.alert_ids or [])
            if alert_id not in alert_ids:
                alert_ids.append(alert_id)
                group.alert_ids = alert_ids
                db.commit()

correlation_engine = EventCorrelationEngine()
