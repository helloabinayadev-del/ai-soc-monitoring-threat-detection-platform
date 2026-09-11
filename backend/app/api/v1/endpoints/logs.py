from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.log import LogEvent
from app.models.alert import SecurityAlert
from app.models.threat_intel import ThreatIntel
from app.models.ml_prediction import MLPrediction
from app.schemas.log import LogEventCreate, LogEventResponse
from app.ml.anomaly_detector import ml_anomaly_detector
from app.ai.threat_classifier import threat_classifier
from app.services.prioritization_service import prioritization_service
from app.services.correlation_engine import correlation_engine
from app.websockets.connection_manager import ws_manager
from app.services.audit_service import audit_service

router = APIRouter()

@router.post("/", response_model=LogEventResponse)
async def ingest_log(log_in: LogEventCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    log_dict = log_in.model_dump()
    now_utc = datetime.now(timezone.utc)

    # 1. Fetch recent history for feature engineering context
    history_logs = db.query(LogEvent).order_by(LogEvent.timestamp.desc()).limit(100).all()
    history_dicts = [
        {"source_ip": l.source_ip, "action": l.action, "raw_message": l.raw_message}
        for l in history_logs
    ]

    # 2. Run Scikit-Learn Isolation Forest ML Anomaly Detection
    ml_result = ml_anomaly_detector.predict(log_dict, history=history_dicts)
    is_anomaly = ml_result["prediction"]
    anomaly_score = ml_result["anomaly_score"]
    model_ver = ml_result["model_version"]

    # 3. Create initial LogEvent record
    db_log = LogEvent(
        **log_dict,
        timestamp=now_utc,
        anomaly_score=anomaly_score,
        is_anomaly=is_anomaly,
        model_version=model_ver,
        feature_vector=ml_result["raw_features"]
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    # 3b. Persist MLPrediction record
    db_ml_pred = MLPrediction(
        event_id=db_log.id,
        model_version=model_ver,
        anomaly_score=anomaly_score,
        prediction=is_anomaly,
        threshold=ml_result.get("threshold", 65.0),
        contributing_features=ml_result.get("contributing_features")
    )
    db.add(db_ml_pred)
    db.commit()

    # 4. Run SIEM Threat Rule Classifier
    matched_rule = threat_classifier.classify_log(db_log.raw_message, db_log.parsed_fields)

    # 5. Run Event Correlation Engine
    corr_group = correlation_engine.correlate_event(db, db_log, matched_rule)
    corr_id = corr_group.correlation_id if corr_group else f"CORR-{now_utc.strftime('%Y%m%d%H%M%S')}"

    # 6. Check Threat Intelligence Match
    intel_match = False
    if db_log.source_ip:
        intel_match = db.query(ThreatIntel).filter(ThreatIntel.ioc_value == db_log.source_ip).first() is not None

    # 7. Generate SIEM Alert if rule matched OR anomalous score threshold exceeded
    if matched_rule or is_anomaly == "ANOMALOUS":
        severity = matched_rule["severity"] if matched_rule else ("HIGH" if anomaly_score >= 80 else "MEDIUM")
        title = matched_rule["title"] if matched_rule else f"ML Anomaly Detected (Score {anomaly_score:.1f}/100)"
        cat = matched_rule["category"] if matched_rule else "ML Anomaly Detection"
        rule_id = matched_rule["rule_id"] if matched_rule else "AI-ANOMALY-001"
        tactic = matched_rule["mitre_tactic"] if matched_rule else "TA0007 - Discovery"
        tech = matched_rule["mitre_technique"] if matched_rule else "T1082 - System Information Discovery"

        # Determine Detection Source Tag
        if matched_rule and is_anomaly == "ANOMALOUS":
            det_source = "HYBRID"
        elif matched_rule:
            det_source = "RULE_BASED"
        else:
            det_source = "ML_ANOMALY"

        # 8. Calculate Intelligent Prioritization Risk Score
        risk_res = prioritization_service.calculate_risk(
            severity=severity,
            anomaly_score=anomaly_score,
            matched_rule=matched_rule,
            source_ip=db_log.source_ip,
            affected_asset=db_log.hostname or "Internal Workstation",
            threat_intel_match=intel_match,
            correlated_event_count=corr_group.event_count if corr_group else 1,
            frequency_count=len([h for h in history_dicts if h.get("source_ip") == db_log.source_ip]) + 1
        )

        new_alert = SecurityAlert(
            title=title,
            description=f"Detection ({det_source}) triggered for log event ID #{db_log.id}: {db_log.raw_message[:150]}",
            rule_id=rule_id,
            severity=severity,
            category=cat,
            mitre_tactic=tactic,
            mitre_technique=tech,
            source_ip=db_log.source_ip,
            destination_ip=db_log.destination_ip,
            affected_asset=db_log.hostname or "Internal Workstation",
            risk_score=risk_res["risk_score"],
            priority=risk_res["priority"],
            detection_source=det_source,
            risk_factors=risk_res["contributing_factors"],
            anomaly_score=anomaly_score,
            status="NEW",
            raw_payload={"log_id": db_log.id, "raw_message": db_log.raw_message, "ml_details": ml_result},
            correlation_id=corr_id,
            source_event_ids=[db_log.id]
        )
        db.add(new_alert)
        db.commit()
        db.refresh(new_alert)

        # Link alert to correlation group
        if corr_group:
            correlation_engine.link_alert_to_correlation(db, corr_id, new_alert.id)

        # Broadcast WebSocket alert notification
        background_tasks.add_task(ws_manager.broadcast, {
            "type": "NEW_ALERT",
            "alert": {
                "id": new_alert.id,
                "title": new_alert.title,
                "severity": new_alert.severity,
                "priority": new_alert.priority,
                "risk_score": new_alert.risk_score,
                "detection_source": det_source,
                "correlation_id": corr_id
            }
        })

    # Broadcast WebSocket log notification
    background_tasks.add_task(ws_manager.broadcast, {
        "type": "NEW_LOG",
        "log": {
            "id": db_log.id,
            "timestamp": db_log.timestamp.isoformat(),
            "source": db_log.log_source,
            "event_type": db_log.event_type,
            "severity": db_log.severity,
            "is_anomaly": db_log.is_anomaly,
            "anomaly_score": anomaly_score,
            "correlation_id": corr_id
        }
    })

    # Audit Trail
    audit_service.record_action(
        db=db,
        actor_username="system_ingest",
        action="LOG_INGEST",
        resource_type="LogEvent",
        resource_id=db_log.id,
        details=f"Ingested {db_log.log_source} log event ID #{db_log.id} ({db_log.event_type}) - Correlation {corr_id}"
    )

    return db_log

@router.post("/simulate-scenario")
async def simulate_scenario(scenario_type: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    scenarios = {
        "brute_force": LogEventCreate(
            log_source="WindowsEvent",
            event_type="Authentication",
            source_ip="192.168.1.105",
            destination_ip="10.0.0.5",
            source_port=49201,
            destination_port=445,
            user_name="admin",
            hostname="WKSTN-FIN-02",
            action="FAIL",
            severity="HIGH",
            raw_message="EventID 4625: Account failed to log on. Invalid password attempt from 192.168.1.105 (failed login attempt)"
        ),
        "privilege_escalation": LogEventCreate(
            log_source="LinuxSyslog",
            event_type="PrivilegeEscalation",
            source_ip="10.0.4.12",
            destination_ip="10.0.4.12",
            source_port=50221,
            destination_port=22,
            user_name="developer",
            hostname="SRV-APP-PROD01",
            action="EXECUTE",
            severity="CRITICAL",
            raw_message="sudo: developer : TTY=pts/1 ; PWD=/tmp ; USER=root ; COMMAND=/usr/bin/python3 -c 'import pty; pty.spawn(\"/bin/bash\")' (root access privilege escalation)"
        ),
        "powershell_stager": LogEventCreate(
            log_source="EndpointEDR",
            event_type="ProcessCreation",
            source_ip="10.0.2.88",
            destination_ip="10.0.2.88",
            source_port=0,
            destination_port=0,
            user_name="SYSTEM",
            hostname="DC-PRIMARY-01",
            action="EXECUTE",
            severity="HIGH",
            raw_message="CrowdStrike EDR: powershell.exe -ExecutionPolicy Bypass -NoProfile -EncodedCommand SQBFAAX... (downloadstring iex bypass)"
        ),
        "c2_beacon": LogEventCreate(
            log_source="Firewall",
            event_type="NetworkConnection",
            source_ip="10.0.1.50",
            destination_ip="198.51.100.45",
            source_port=54312,
            destination_port=443,
            user_name="a.davis",
            hostname="WKSTn-HR-09",
            action="ALLOW",
            severity="HIGH",
            raw_message="PaloAlto FW: Outbound HTTPS session established to suspicious external host 198.51.100.45:443 (c2 server beacon)"
        ),
        "sqli_attack": LogEventCreate(
            log_source="AWSCloudTrail",
            event_type="Authentication",
            source_ip="203.0.113.88",
            destination_ip="172.31.0.1",
            source_port=443,
            destination_port=443,
            user_name="anonymous",
            hostname="AWS-US-EAST-1",
            action="FAIL",
            severity="CRITICAL",
            raw_message="WAF WebACL Log: HTTP GET /api/v1/users?id=1' UNION SELECT username, password FROM users-- (sqli injection attempt)"
        )
    }

    log_in = scenarios.get(scenario_type.lower(), scenarios["brute_force"])
    return await ingest_log(log_in, background_tasks, db)

@router.get("/", response_model=List[LogEventResponse])
def get_logs(
    skip: int = 0,
    limit: int = 50,
    source: Optional[str] = None,
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    source_ip: Optional[str] = None,
    user_name: Optional[str] = None,
    hostname: Optional[str] = None,
    correlation_id: Optional[str] = None,
    anomaly_only: bool = False,
    min_anomaly_score: Optional[float] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(LogEvent)
    if source and source != "ALL":
        query = query.filter(LogEvent.log_source == source)
    if severity and severity != "ALL":
        query = query.filter(LogEvent.severity == severity)
    if event_type and event_type != "ALL":
        query = query.filter(LogEvent.event_type == event_type)
    if source_ip:
        query = query.filter(LogEvent.source_ip == source_ip)
    if user_name:
        query = query.filter(LogEvent.user_name == user_name)
    if hostname:
        query = query.filter(LogEvent.hostname == hostname)
    if correlation_id:
        query = query.filter(LogEvent.correlation_id == correlation_id)
    if anomaly_only:
        query = query.filter(LogEvent.is_anomaly == "ANOMALOUS")
    if min_anomaly_score is not None:
        query = query.filter(LogEvent.anomaly_score >= min_anomaly_score)
    if search:
        s_term = f"%{search}%"
        query = query.filter(
            (LogEvent.raw_message.ilike(s_term)) |
            (LogEvent.source_ip.ilike(s_term)) |
            (LogEvent.destination_ip.ilike(s_term)) |
            (LogEvent.user_name.ilike(s_term)) |
            (LogEvent.hostname.ilike(s_term)) |
            (LogEvent.correlation_id.ilike(s_term))
        )
    return query.order_by(LogEvent.timestamp.desc()).offset(skip).limit(limit).all()
