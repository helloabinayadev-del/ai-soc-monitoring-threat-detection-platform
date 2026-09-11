# Security Audit Trail & Access Control Specification

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Audit Trail Logging, Data Retention, & Access Control Policies  

---

## 1. Audited Security Actions

All security-sensitive administrative and analyst actions persist in the `audit_logs` table (`app/models/audit_log.py`):

| Action Type | Resource Type | Description | Audited Metadata |
|---|---|---|---|
| `LOGIN` | User | Successful user authentication | Username, IP address, Timestamp, Result (`SUCCESS`) |
| `FAILED_LOGIN` | User | Failed authentication attempt | Username, IP address, Timestamp, Result (`FAILED`) |
| `LOGOUT` | User | User session termination | Username, IP address, Timestamp, Result (`SUCCESS`) |
| `ALERT_VIEWED` | SecurityAlert | Analyst opening alert details | Username, Alert ID, Risk Score, Priority |
| `ALERT_STATUS_CHANGED` | SecurityAlert | Triage status update | Username, Alert ID, Old Status $\rightarrow$ New Status |
| `INCIDENT_CREATED` | Incident | New incident ticket creation | Username, Incident ID, Correlation ID |
| `INCIDENT_RESOLVED` | Incident | Incident resolution | Username, Incident ID, Resolution Notes |
| `ANALYST_FEEDBACK` | AnalystFeedback | Feedback label submission | Username, Alert ID, Label (`TRUE_POSITIVE` / `FALSE_POSITIVE`) |
| `ML_THRESHOLD_UPDATE` | MLPrediction | Anomaly threshold tuning | Username, Old Threshold $\rightarrow$ New Threshold |
| `EXPORT_GENERATED` | Report | Security summary report export | Username, Export Format (JSON / Markdown) |

---

## 2. What Is NOT Logged (Security Safeguards)

To protect system credentials and comply with data privacy standards:
- **Plaintext Passwords**: Never stored or logged under any circumstances.
- **JWT Secret Keys / Hashes**: Excluded from all application loggers.
- **Session Tokens**: Stripped from audit payloads.

---

## 3. RBAC Access Control Policy

- **`GET /api/v1/audit/`**: Restricted strictly to authorized roles (`Admin`, `Analyst`, `Auditor`) via FastAPI `require_roles` dependency.
- Read-only users (`Viewer`) cannot view security audit trails.
