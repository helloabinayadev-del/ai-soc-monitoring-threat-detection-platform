# Controlled Real-Time SOC Laboratory Demonstration

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Scenario**: Dual-Browser Real-Time Event Ingestion & Alert Broadcast (Lab Telemetry Data)  

> **Note**: All real-time streaming events use synthetic laboratory simulation data.

---

## Controlled Demonstration Steps (6 Steps)

### Step 1: Client Connection Setup
- **Browser A**: Open SOC Dashboard at `http://localhost:5173`. Connection indicator displays `● LIVE` (`ws://localhost:8000/ws/soc-stream`).
- **Browser B / API Client**: Log submission producer (`POST /api/v1/logs/`).

### Step 2: Ingest Security Event (Browser B)
- Browser B submits a LAB security log event (`log_source: Firewall`, `event_type: Authentication`, `severity: HIGH`, `source_ip: 198.51.100.88`).

### Step 3: Real-Time Log Broadcast
- Backend persists log to DB and publishes `NEW_SECURITY_EVENT` envelope via `ws_manager`.
- Browser A immediately receives event packet and prepends it to the **Live Event Logs** table without requiring a page refresh.

### Step 4: Real-Time SIEM Alert Broadcast
- Detection Engine triggers `RULE-001` (`HYBRID` detection source, Risk Score `88.5`, Priority `HIGH`).
- Backend publishes `NEW_ALERT` envelope.
- Browser A displays non-blocking toast notification: *"NEW HIGH-SEVERITY ALERT: Multiple Failed Logins (Brute Force)"*.

### Step 5: Incident Escalation Stream
- Analyst creates Incident ticket in Browser A.
- Backend publishes `INCIDENT_CREATED` envelope. UI updates incident queue status dynamically.

### Step 6: Reconnection & Recovery Verification
- Momentarily disconnect network or close WebSocket connection in Browser A; indicator displays `RECONNECTING`.
- Upon network restoration, Browser A reconnects, fetches latest alerts via `GET /api/v1/alerts/`, and resumes `● LIVE` streaming.
