# End-to-End Threat Investigation Workflow Specification

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Threat Hunting & Investigation Lifecycle  

---

## 1. Complete Investigation Workflow

```
[ Log Ingestion Stream ]
          ↓
[ Threat Hunting Search / Parameterized Filter ]
          ↓
[ Event Detail Triage & Related Event Discovery ]
          ↓
[ Multi-Stage Correlation Chain Review (CORR-YYYYMMDD-XXXX) ]
          ↓
[ SIEM Alert & Risk Score Inspection (0-100 Score & Factors) ]
          ↓
[ Grounded AI Copilot Investigation Query ]
          ↓
[ Incident Case Creation & Evidence Linking ]
          ↓
[ Analyst Feedback Submission & Ticket Resolution ]
          ↓
[ Audit Trail Recording & Analytics Summary ]
```

---

## 2. Step-by-Step Triage Stages

1. **Telemetry Search**: Analyst identifies suspicious activity via parameterized filters on `source_ip`, `user_name`, or `hostname`.
2. **Evidence Discovery**: Analyst inspects raw logs, 10 extracted security features, and Isolation Forest anomaly scores.
3. **Correlation Timeline Review**: Analyst views chronological multi-stage attack events linked under `CORR-YYYYMMDD-XXXX`.
4. **Transparent Risk Inspection**: Analyst opens the **Risk Breakdown** drawer to review contributing factor weights.
5. **AI Copilot Triage**: Copilot generates a 10-point evidence analysis distinguishing `FACT` from `INFERENCE`.
6. **Incident Escalation**: Analyst creates an Incident case ticket (`OPEN` $\rightarrow$ `INVESTIGATING` $\rightarrow$ `RESOLVED`).
7. **Analyst Feedback & Audit Logging**: Analyst submits feedback label (`TRUE_POSITIVE` / `FALSE_POSITIVE`), automatically logged in the audit trail.
