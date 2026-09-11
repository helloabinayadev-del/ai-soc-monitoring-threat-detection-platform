# Controlled SOAR Laboratory Demonstration Scenario

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Scenario**: Brute Force Attack Investigation & Automated Response (Lab Simulation Data)  

> **Note**: All events and response actions in this scenario use synthetic laboratory simulation telemetry.

---

## Controlled Demonstration Steps (10 Steps)

### Step 1: Lab Log Event Ingestion
- Ingest 5 failed login logs from Source IP `198.51.100.99` targeting asset `DC-PRIMARY-01`.

### Step 2: Signature & ML Detection
- MITRE ATT&CK rule `RULE-001` matches; Isolation Forest calculates Anomaly Score `88.5/100` (`ANOMALOUS`). Detection Source: `HYBRID`.

### Step 3: Multi-Factor Risk Prioritization
- Risk Engine calculates Risk Score `92.4/100` and assigns Priority `CRITICAL`.

### Step 4: Event Correlation
- Correlation Engine groups events under `CORR-20260827-0001` (`Brute Force Attack Pattern`).

### Step 5: SIEM Alert Generation
- Alert #12 generated with Priority `CRITICAL`, `detection_source: HYBRID`, and `correlation_id: CORR-20260827-0001`.

### Step 6: AI Copilot Playbook Recommendation
- Copilot evaluates alert evidence and recommends Playbook `PB-001` (*Brute Force Attack Investigation & Containment*).

### Step 7: Playbook Execution Preview
- Analyst clicks **Execute Playbook**. Steps 1–3 execute automatically (Evidence Collection, Threat Intel Lookup, AI Summary Generation).

### Step 8: Human Approval Request
- Step 4 (`REQUEST_ANALYST_APPROVAL`) pauses execution at state `PENDING_APPROVAL`. UI displays: *"Analyst approval required to block IP 198.51.100.99"*.

### Step 9: Analyst Action Approval & Lab Simulation
- Analyst clicks **Approve Action**. Step 5 executes: `SIMULATED ACTION: Firewall block rule applied for IP 198.51.100.99 (Approved by analyst)`. Status updates to `COMPLETED`.

### Step 10: Audit Trail Recording
- Audit log records `PLAYBOOK_EXECUTED` and `ACTION_APPROVED` entries in the `audit_logs` table.
