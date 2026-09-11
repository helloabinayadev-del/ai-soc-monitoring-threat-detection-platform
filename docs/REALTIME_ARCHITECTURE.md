# Real-Time Event Streaming Architecture Specification

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: WebSocket Protocol, Event Envelopes, & Reconnection Recovery  

---

## 1. Event Pipeline Architecture

```
[ Log Producer / Producer Script ]
                ↓
[ REST API Ingestion Endpoint (/api/v1/logs/) ]
                ↓
[ Database Persistence (LogEvent Record Saved) ]
                ↓
[ Detection + ML + Risk + Correlation Pipeline ]
                ↓
[ WebSocket Connection Manager (ws_manager.broadcast) ]
                ↓ (Sub-10ms Event Delivery)
[ React 18 SOC Dashboard (ws://localhost:8000/ws/soc-stream) ]
```

---

## 2. Standardized Event Envelope & Supported Event Types

All real-time notifications use a consistent event envelope:

```json
{
  "event_type": "NEW_ALERT",
  "event_id": "EVT-A1B2C3D4",
  "timestamp": "2026-08-28T07:05:00.000Z",
  "payload": {
    "id": 14,
    "title": "Multiple Failed Logins (Brute Force)",
    "severity": "HIGH",
    "priority": "HIGH",
    "risk_score": 88.5,
    "detection_source": "HYBRID",
    "correlation_id": "CORR-20260828-0001"
  }
}
```

### Supported Real-Time Event Types:
- `NEW_SECURITY_EVENT`: Published when a raw log is ingested and normalized.
- `NEW_ALERT`: Published when a SIEM alert is generated.
- `ALERT_UPDATED`: Published when an alert status changes (`NEW` $\rightarrow$ `INVESTIGATING`).
- `INCIDENT_CREATED`: Published when an incident case ticket is created.
- `CORRELATION_CREATED`: Published when a multi-stage correlation group is updated.
- `SYSTEM_HEALTH_CHANGED`: Published when a subsystem health state changes.
- `PLAYBOOK_EXECUTION_UPDATED`: Published when a SOAR response playbook executes.

---

## 3. Payload Sanitization & Security

- **Credential Stripping**: Sensitive keys (`password`, `access_token`, `secret_key`) are stripped prior to broadcasting.
- **Source of Truth**: REST APIs (`/api/v1/`) serve as the source of truth for persisted state. If the WebSocket stream disconnects, the frontend automatically re-queries REST endpoints upon reconnection to restore state.
