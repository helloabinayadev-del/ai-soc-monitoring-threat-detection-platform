# Controlled SOC Lab Demonstration Walkthrough

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Scenario**: Multi-Stage APT Attack Chain Demonstration (Lab Test Data)  

> **Note**: All events in this demonstration use synthetic laboratory test telemetry.

---

## Demonstration Sequence (18 Steps)

### Step 1: User Login
- Log into platform at `http://localhost:5173` using `admin` / `Admin@123`.

### Step 2: Ingest Stage 1 — Brute Force Authentication Failures
- Ingest 5 consecutive failed login logs from Source IP `198.51.100.99` targeting user `admin` via `POST /api/v1/logs/` or Scenario Simulator.

### Step 3: Ingest Stage 2 — Successful Login
- Ingest 1 successful authentication log from `198.51.100.99` for user `admin`.

### Step 4: Ingest Stage 3 — Privilege Escalation
- Ingest suspicious `sudo` privilege escalation log execution (`sudo /usr/bin/python3 -c 'import pty; pty.spawn("/bin/bash")'`).

### Step 5: Ingest Stage 4 — PowerShell Stager Execution
- Ingest Endpoint EDR log with encoded PowerShell download string (`powershell.exe -ExecutionPolicy Bypass -EncodedCommand SQBFAAX...`).

### Step 6: Ingest Stage 5 — Outbound C2 Beaconing
- Ingest Firewall network connection log connecting to known malicious C2 IP on port `4444`.

### Step 7: Automated Log Processing & Feature Extraction
- Backend extracts 10 security features per log (`failed_login_count=5`, `is_failed_auth=1.0`, `severity_numeric=5`).

### Step 8: Scikit-Learn Isolation Forest ML Prediction
- Isolation Forest calculates Anomaly Score **88.5 / 100** (`prediction: ANOMALOUS`) with feature z-score attributions.

### Step 9: Event Correlation Engine Grouping
- Engine matches entity `198.51.100.99` across 30-minute window and generates Correlation ID `CORR-20260827-0001` with pattern `Potential Multi-Stage Attack Pattern`.

### Step 10: Multi-Factor Risk Prioritization
- Risk engine computes Risk Score **92.4 / 100** and assigns Priority **CRITICAL**.

### Step 11: SIEM Alert Creation
- Alert #12 created with `detection_source: HYBRID`, priority `CRITICAL`, and `correlation_id: CORR-20260827-0001`.

### Step 12: View Live Event Logs Page
- Open **Live Event Logs** tab (`/logs`); observe anomaly badges (`ANOMALOUS - Score 88.5`) and model version (`IsolationForest-v1.2`).

### Step 13: View SIEM Alerts Queue
- Open **SIEM Alerts** tab (`/alerts`); observe Alert #12 with Red `CRITICAL` priority badge and `Src: HYBRID` tag.

### Step 14: Inspect Transparent Risk Breakdown
- Click the Info icon on Alert #12 to open the **Risk Score Breakdown** drawer. Observe itemized list: Rule score, ML score, frequency burst, asset weight (`DC-PRIMARY-01`), and correlation weight.

### Step 15: View Correlation Attack Chain
- Open **Incidents / Correlation Chains** tab (`/incidents`); view `CORR-20260827-0001` chronological attack timeline (Authentication Failure $\rightarrow$ Success $\rightarrow$ Priv Esc $\rightarrow$ Execution $\rightarrow$ C2).

### Step 16: AI Security Copilot Investigation
- Click **Investigate with AI Copilot**; Copilot generates grounded 10-point analysis with explicit `FACT`, `INFERENCE`, `RECOMMENDATION`, and `UNCERTAINTY` sections.

### Step 17: Incident Triage & Analyst Action
- Click **Create Incident Ticket**; update status from `NEW` to `INVESTIGATING` and submit analyst feedback (`TRUE_POSITIVE`).

### Step 18: View Quantitative Analytics
- Open **Analytics** tab (`/analytics`); observe Baseline vs AI/ML Detection comparison table (**94.2% Precision**, **12.5s MTTD**).
