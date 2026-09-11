# Phase 1 — Threat Hunting Capability Audit Report

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Audit Scope**: Threat Hunting Workspace & Evidence Discovery Architecture  
**Date**: August 27, 2026  

---

## 1. Reusable Systems & Telemetry Audit

| Platform Component | Existing Schema / API | Reusability Status | Evidence |
|---|---|---|---|
| **Security Logs** | `LogEvent` (`log_events`) | Reused directly | Indexed by `source_ip`, `user_name`, `hostname`, `correlation_id`, `timestamp`. |
| **SIEM Alerts** | `SecurityAlert` (`security_alerts`) | Reused directly | Linked to `source_event_ids` and `correlation_id`. |
| **Event Correlation** | `CorrelationGroup` (`correlation_groups`) | Reused directly | Groups related multi-stage logs under `CORR-YYYYMMDD-XXXX`. |
| **Incident Response** | `Incident` (`incidents`) | Reused directly | Manages investigation tickets and status transitions. |
| **Threat Intelligence** | `ThreatIntel` (`threat_intel`) | Reused directly | Provides IP, domain, and hash lookup matches. |
| **ML Anomaly Predictions**| `MLPrediction` (`ml_predictions`) | Reused directly | Provides feature z-score attributions per log event. |
| **AI Security Copilot** | `SecurityCopilotService` | Reused directly | Grounded 10-point evidence investigation queries. |
| **RBAC / Security** | `require_roles` dependency | Reused directly | Protects threat-hunting queries and incident creation. |

---

## 2. API Endpoints for Threat Hunting
- `GET /api/v1/logs/`: Extended with parameterized filters (`source_ip`, `user_name`, `hostname`, `correlation_id`, `event_type`, `min_anomaly_score`, `search`).
- `GET /api/v1/alerts/`: Extended with `priority`, `detection_source`, and `min_risk_score` filters.
- `GET /api/v1/correlations/{correlation_id}`: Retrieves complete attack timeline.
- `POST /api/v1/copilot/query`: Executes grounded 10-point investigation queries.
- `POST /api/v1/incidents/`: Creates investigation cases linked to correlation chains.
