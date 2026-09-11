# Controlled Case Investigation Laboratory Demonstration

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Scenario**: Brute-Force Authentication Investigation & Forensic Report Generation (Lab Simulation Telemetry)  

> **Note**: All case evidence and investigation artifacts use synthetic laboratory simulation data.

---

## Controlled Demonstration Steps (8 Steps)

### Step 1: SIEM Alert Ingestion
- SIEM Alert #12 (`Multiple Failed Logins (Brute Force)`, Priority `HIGH`, Correlation `CORR-20260828-0001`).

### Step 2: Case Creation
- Analyst creates Incident Case ticket `INC-A1B2C3` linked to Alert #12 (`POST /api/v1/incidents/`).

### Step 3: Analyst Assignment
- Assign case to analyst `analyst_user` (`PUT /api/v1/incidents/1/assign`). Status transitions to `IN_PROGRESS`.

### Step 4: Attach Forensic Evidence & Compute SHA-256
- Analyst attaches raw Windows Security Event 4625 log telemetry (`POST /api/v1/incidents/1/evidence`).
- Platform calculates SHA-256 hash: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

### Step 5: Grounded AI Copilot Triage
- Copilot evaluates attached evidence and generates grounded remediation steps.

### Step 6: SOAR Containment Playbook Execution
- Execute EDR host isolation containment action (`POST /api/v1/incidents/1/containment-action?action_type=ISOLATE_HOST`). Status updates to `CONTAINMENT`.

### Step 7: Analyst Finding Decision & Closure
- Analyst sets finding outcome to `CONFIRMED` and closes case (`status: RESOLVED`).

### Step 8: Forensic Report Export & Hash Verification
- Export forensic report (`GET /api/v1/incidents/1/report`). Report displays `sha256_report_hash` and clear section headers (`ANALYST FINDINGS` vs `AI-GENERATED CONTENT`).
