# System Observability & Operational Health Specification

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Operational Visibility, System Health, & Failure Diagnostics  

---

## 1. Centralized System Health Architecture

The platform monitors 8 core services via `GET /api/v1/health`:

| Subsystem Component | Health Check Target | Normal Response | Failure / Degraded State |
|---|---|---|---|
| **Backend Server** | REST API Routing | `HEALTHY` (Response time <5ms) | `UNAVAILABLE` (Process crash / HTTP 500) |
| **Database** | SQLite / PostgreSQL ORM (`SELECT 1`) | `HEALTHY` (Query time <2ms) | `UNAVAILABLE` (File lock / DB connection fail) |
| **Isolation Forest ML** | Model fit status & parameters | `HEALTHY` (`model_version: IsolationForest-v1.2`) | `DEGRADED` (Model uninitialized) |
| **AI Security Copilot** | 10-point evidence engine | `HEALTHY` (`engine: Evidence-Driven-Copilot-v2.0`) | `DEGRADED` (Copilot service unavailable) |
| **Threat Intelligence** | Local IOC database count | `HEALTHY` (IOC count loaded) | `UNAVAILABLE` (IOC DB table unreachable) |
| **Log Ingestion Engine**| Event stream processed count | `HEALTHY` (Total events & latest timestamp) | `UNAVAILABLE` (Ingestion endpoint failure) |
| **Detection Engine** | Signature rules classifier | `HEALTHY` (Active rules count: 7) | `DEGRADED` (Rules engine warning) |
| **Correlation Engine** | Active correlation groups | `HEALTHY` (Active correlation count) | `UNAVAILABLE` (Correlation query failure) |

---

## 2. Overall Health Status Classifications

- **`HEALTHY`**: All 8 critical and optional services are online and fully operational.
- **`DEGRADED`**: Core log ingestion and database persistence are operational, but an optional dependency (AI Copilot or Threat Intel) is temporarily unavailable or uninitialized.
- **`UNAVAILABLE`**: Database connection failure or API routing crash preventing core SOC operations.

---

## 3. Graceful Dependency Failure Handling

The system strictly decouples application failures from optional dependency degradation:
- **AI Service Failure**: If the AI Security Copilot service fails or times out, SIEM alert generation and ML anomaly detection continue unaffected. The UI renders `"AI analysis temporarily unavailable"` without fabricating synthetic responses.
- **Threat Intelligence Failure**: If the IOC database is unreachable, alert generation defaults to `"Threat Intelligence lookup unavailable"` (+0 pts contribution) without failing log ingestion.
- **ML Engine Failure**: If the Isolation Forest model is uninitialized, rule-based signature detection (`RULE_BASED`) continues operating independently.
