from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import random

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.log import LogEvent
from app.models.alert import SecurityAlert
from app.models.incident import Incident
from app.models.threat_intel import ThreatIntel
from app.ai.anomaly_detector import anomaly_detector

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            admin_user.hashed_password = get_password_hash("Admin@123")
            admin_user.email = "admin@socplatform.com"
            admin_user.role = "SOC_ADMIN"
            db.commit()
            print("[+] Updated existing Admin user password to Admin@123.")
        else:
            admin_user = User(
                email="admin@socplatform.com",
                username="admin",
                hashed_password=get_password_hash("Admin@123"),
                full_name="SOC Lead Administrator",
                role="SOC_ADMIN"
            )
            db.add(admin_user)
            db.commit()
            print("[+] Seeded Admin user with Admin@123.")

        if not db.query(User).filter(User.username == "analyst").first():
            analyst_user = User(
                email="analyst@socplatform.com",
                username="analyst",
                hashed_password=get_password_hash("AnalystSec2026!"),
                full_name="Senior Security Analyst",
                role="SOC_ANALYST"
            )
            db.add(analyst_user)
            db.commit()
            print("[+] Seeded Analyst user.")

        if not db.query(User).filter(User.username == "responder").first():
            responder_user = User(
                email="responder@socplatform.com",
                username="responder",
                hashed_password=get_password_hash("ResponderSec2026!"),
                full_name="Incident Response Lead",
                role="INCIDENT_RESPONDER"
            )
            db.add(responder_user)
            db.commit()
            print("[+] Seeded Incident Responder user.")

        if not db.query(User).filter(User.username == "viewer").first():
            viewer_user = User(
                email="viewer@socplatform.com",
                username="viewer",
                hashed_password=get_password_hash("ViewerSec2026!"),
                full_name="Security Operations Viewer",
                role="SECURITY_VIEWER"
            )
            db.add(viewer_user)
            db.commit()
            print("[+] Seeded Security Viewer user.")


        # 2. Seed Threat Intel Feeds
        if db.query(ThreatIntel).count() == 0:
            iocs = [
                ThreatIntel(ioc_value="198.51.100.45", ioc_type="IP", threat_type="Command & Control", threat_score=92.0, source_feed="AlienVault OTX", description="Known Cobalt Strike C2 server"),
                ThreatIntel(ioc_value="203.0.113.109", ioc_type="IP", threat_type="Botnet", threat_score=85.0, source_feed="AbuseIPDB", description="Mirai Botnet scanner node"),
                ThreatIntel(ioc_value="e3b0c44298fc1c149afbf4c8996fb924", ioc_type="MD5", threat_type="Ransomware", threat_score=99.0, source_feed="VirusTotal", description="LockBit 3.0 Encryptor Payload"),
                ThreatIntel(ioc_value="phishing-bank-update.xyz", ioc_type="DOMAIN", threat_type="Phishing", threat_score=78.0, source_feed="PhishTank", description="Credential harvesting domain")
            ]
            db.add_all(iocs)
            db.commit()
            print("[+] Seeded Threat Intelligence feeds.")

        # 3. Seed Security Event Logs
        if db.query(LogEvent).count() == 0:
            sample_logs = [
                {"log_source": "WindowsEvent", "event_type": "Authentication", "source_ip": "192.168.1.105", "destination_ip": "10.0.0.5", "source_port": 49201, "destination_port": 445, "user_name": "j.smith", "hostname": "WKSTn-FIN-02", "action": "FAIL", "severity": "HIGH", "raw_message": "EventID 4625: Account failed to log on. Invalid password attempt from 192.168.1.105"},
                {"log_source": "LinuxSyslog", "event_type": "PrivilegeEscalation", "source_ip": "10.0.4.12", "destination_ip": "10.0.4.12", "source_port": 50221, "destination_port": 22, "user_name": "developer", "hostname": "SRV-APP-PROD01", "action": "EXECUTE", "severity": "CRITICAL", "raw_message": "sudo: developer : TTY=pts/1 ; PWD=/tmp ; USER=root ; COMMAND=/usr/bin/python3 -c 'import pty; pty.spawn(\"/bin/bash\")'"},
                {"log_source": "Firewall", "event_type": "NetworkConnection", "source_ip": "10.0.1.50", "destination_ip": "198.51.100.45", "source_port": 54312, "destination_port": 443, "user_name": "a.davis", "hostname": "WKSTn-HR-09", "action": "ALLOW", "severity": "HIGH", "raw_message": "PaloAlto FW: Outbound HTTPS session established to suspicious external host 198.51.100.45:443"},
                {"log_source": "EndpointEDR", "event_type": "ProcessCreation", "source_ip": "10.0.2.88", "destination_ip": "10.0.2.88", "source_port": 0, "destination_port": 0, "user_name": "SYSTEM", "hostname": "DC-PRIMARY-01", "action": "EXECUTE", "severity": "HIGH", "raw_message": "CrowdStrike: powershell.exe -ExecutionPolicy Bypass -NoProfile -EncodedCommand SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAA='"},
                {"log_source": "AWSCloudTrail", "event_type": "Authentication", "source_ip": "54.210.12.8", "destination_ip": "172.31.0.1", "source_port": 443, "destination_port": 443, "user_name": "cloud-admin", "hostname": "AWS-US-EAST-1", "action": "SUCCESS", "severity": "INFORMATIONAL", "raw_message": "CloudTrail: ConsoleLogin success for user cloud-admin from MFA device arn:aws:iam::123456789:mfa/cloud-admin"}
            ]
            
            for idx, log_data in enumerate(sample_logs, 1):
                is_anomaly, score = anomaly_detector.predict(log_data)
                log_obj = LogEvent(
                    **log_data,
                    timestamp=datetime.now(timezone.utc) - timedelta(minutes=random.randint(5, 120)),
                    anomaly_score=score,
                    is_anomaly=is_anomaly,
                    correlation_id=f"CORR-SEED-00{idx}"
                )
                db.add(log_obj)
            db.commit()
            print("[+] Seeded Security Event Logs.")

        # 4. Seed Security Alerts
        if db.query(SecurityAlert).count() == 0:
            alerts = [
                SecurityAlert(
                    title="Suspicious Encoded PowerShell Execution on Domain Controller",
                    description="EDR telemetry detected powershell.exe spawned with encoded command arguments indicative of Cobalt Strike stager execution.",
                    rule_id="RULE-003",
                    severity="CRITICAL",
                    category="Execution",
                    mitre_tactic="TA0002 - Execution",
                    mitre_technique="T1059.001 - PowerShell",
                    source_ip="10.0.2.88",
                    destination_ip="10.0.2.88",
                    affected_asset="DC-PRIMARY-01",
                    risk_score=92.5,
                    status="NEW",
                    correlation_id="CORR-SEED-004",
                    source_event_ids=[4]
                ),
                SecurityAlert(
                    title="Outbound C2 Beaconing to Malicious IP",
                    description="Firewall logs indicate active bidirectional HTTPS sessions to known C2 server 198.51.100.45.",
                    rule_id="RULE-004",
                    severity="HIGH",
                    category="Command and Control",
                    mitre_tactic="TA0011 - Command and Control",
                    mitre_technique="T1071 - Application Layer Protocol",
                    source_ip="10.0.1.50",
                    destination_ip="198.51.100.45",
                    affected_asset="WKSTn-HR-09",
                    risk_score=88.0,
                    status="INVESTIGATING",
                    correlation_id="CORR-SEED-003",
                    source_event_ids=[3]
                ),
                SecurityAlert(
                    title="Interactive Root Shell Spawned via Sudo Escalation",
                    description="Analyst user 'developer' executed Sudo pty python spawn command to gain root interactive session.",
                    rule_id="RULE-002",
                    severity="CRITICAL",
                    category="Privilege Escalation",
                    mitre_tactic="TA0004 - Privilege Escalation",
                    mitre_technique="T1078 - Valid Accounts",
                    source_ip="10.0.4.12",
                    destination_ip="10.0.4.12",
                    affected_asset="SRV-APP-PROD01",
                    risk_score=95.0,
                    status="NEW",
                    correlation_id="CORR-SEED-002",
                    source_event_ids=[2]
                )
            ]
            db.add_all(alerts)
            db.commit()
            print("[+] Seeded Security Alerts.")

        # 5. Seed Incident Cases
        if db.query(Incident).count() == 0:
            now_utc = datetime.now(timezone.utc)
            incident = Incident(
                incident_number="INC-2026-0891",
                title="Active Adversary Intrusion & Privilege Escalation on Enterprise Domain Controller",
                summary="Multi-stage attack involving credential access, lateral movement, and PowerShell stager execution on DC-PRIMARY-01.",
                severity="CRITICAL",
                status="OPEN",
                assignee="SOC Lead Administrator",
                affected_systems=["DC-PRIMARY-01", "WKSTn-HR-09", "198.51.100.45"],
                mitre_tactics=["TA0002 - Execution", "TA0004 - Privilege Escalation", "TA0011 - Command and Control"],
                ai_recommendation="Isolate DC-PRIMARY-01 and WKSTn-HR-09 immediately. Block 198.51.100.45 on boundary firewall. Reset credentials for user 'a.davis'.",
                correlation_id="CORR-SEED-004",
                alert_ids=[1, 2],
                timeline=[
                    {"time": (now_utc - timedelta(hours=2)).isoformat(), "action": "Incident ticket automatically created from correlated high-risk alerts."},
                    {"time": (now_utc - timedelta(hours=1)).isoformat(), "action": "Assigned to SOC Lead Administrator for emergency triage."}
                ],
                notes=[
                    {"author": "SOC Lead Administrator", "text": "Initial threat vector appears to be stolen admin credentials used to execute encoded PowerShell stager.", "timestamp": now_utc.isoformat()}
                ]
            )
            db.add(incident)
            db.commit()
            print("[+] Seeded Incident Case.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
