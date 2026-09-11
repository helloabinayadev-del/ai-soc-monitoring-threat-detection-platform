# Phase B — Real Event Correlation Engine Implementation Report

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Upgrade Focus**: UPGRADE 3 — REAL EVENT CORRELATION ENGINE  
**Completion Date**: August 27, 2026  

---

## 1. Executive Summary
The Real Event Correlation Engine clusters disparate security logs and SIEM alerts into unified multi-stage attack chains (`CORR-YYYYMMDD-XXXX`). It identifies multi-step adversary behavior across 30-minute sliding windows without creating synthetic or ungrounded correlations.

---

## 2. Architecture & Correlation Flow

```
Security Events (LogEvent)
      ↓
Normalization & Field Matching (Source IP, User, Hostname)
      ↓
30-Minute Sliding Window Grouping
      ↓
Multi-Stage Pattern Matcher (CorrelationEngine)
      ↓
Correlation Group Created (CORR-YYYYMMDD-XXXX)
      ↓
Timeline & Risk Score Enrichment
      ↓
SIEM Alerts & Incidents UI Integration
```

---

## 3. Correlation Criteria & Entity Matching
Logs are grouped when they share at least one primary entity pivot within a 30-minute time window:
- **Primary Pivots**: `source_ip`, `user_name`, `hostname` / `affected_asset`.
- **Secondary Attributes**: `event_type`, `severity`, `anomaly_score`, `threat_intel_match`.

---

## 4. Multi-Stage Attack Sequences
The correlation engine detects multi-stage attack progression patterns:
1. **Brute Force Sequence**: Multiple failed login events (`FAIL`) from same `source_ip` within short time window -> `Potential Brute Force Activity`.
2. **Multi-Stage Attack Sequence**:
   - Stage 1: Failed Login (`Authentication`)
   - Stage 2: Successful Login (`Authentication`)
   - Stage 3: Privilege Escalation (`PrivilegeEscalation`)
   - Stage 4: Discovery / Execution (`ProcessCreation`)
   - Stage 5: Outbound C2 Beacon (`NetworkConnection`)
   -> `Potential Multi-Stage Attack Pattern`

> **Note**: Attack chains are labeled `Potential Multi-Stage Attack Pattern` rather than "Confirmed Attack" until analyst triage.

---

## 5. Correlation ID & Database Schema
- **Correlation ID Format**: `CORR-YYYYMMDD-XXXX` (e.g. `CORR-20260827-0001`).
- **Database Model**: `CorrelationGroup` (`backend/app/models/correlation.py`):
  - `id`: Integer (PK)
  - `correlation_id`: String (Indexed)
  - `pattern_name`: String
  - `primary_entity`: String (`source_ip`, `user_name`, or `hostname`)
  - `entity_value`: String
  - `event_count`: Integer
  - `max_risk_score`: Float
  - `stages_detected`: JSON
  - `status`: String (`OBSERVED`, `INVESTIGATING`, `CONFIRMED`, `DISMISSED`, `RESOLVED`)
  - `first_seen`: DateTime
  - `last_seen`: DateTime
  - `created_at`: DateTime

---

## 6. REST API Endpoints
Implemented in [`backend/app/api/v1/endpoints/correlations.py`](file:///c:/Users/Hello/OneDrive/Desktop/AI-SOC-Monitoring-Platform/backend/app/api/v1/endpoints/correlations.py):
- `GET /api/v1/correlations/`: List active correlation groups.
- `GET /api/v1/correlations/{correlation_id}`: Retrieve detailed correlation object with full attack timeline.
- `PATCH /api/v1/correlations/{correlation_id}/status`: Update correlation status (`OBSERVED`, `INVESTIGATING`, `CONFIRMED`, `DISMISSED`, `RESOLVED`).

---

## 7. Frontend Integration
Updated [`frontend/src/pages/IncidentsPage.tsx`](file:///c:/Users/Hello/OneDrive/Desktop/AI-SOC-Monitoring-Platform/frontend/src/pages/IncidentsPage.tsx) to feature a **Correlation Chains** tab rendering:
- Correlation ID badge (`CORR-YYYYMMDD-XXXX`)
- Pattern Name & Primary Entity
- Stage Progression Stepper UI
- Chronological Attack Timeline with exact timestamps
- Action controls for analyst status updates

---

## 8. Test Verification Results
All correlation engine tests executed successfully in `backend/tests/test_upgraded_pipeline.py` and `backend/tests/test_e2e_attack_pipeline.py`:
- Single entity grouping: **PASSED**
- 30-minute time window boundary enforcement: **PASSED**
- Multi-stage pattern classification: **PASSED**
- Status update API & DB persistence: **PASSED**
