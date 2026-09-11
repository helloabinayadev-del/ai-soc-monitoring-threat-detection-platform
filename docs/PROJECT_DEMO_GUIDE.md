# Project Presentation & Demo Guide

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Presentation Sequence & Screen-by-Screen Walkthrough  

---

## Presentation Sequence (10 Steps)

### Screen 1: Login Page (`/login`)
- **What to Show**: Clean login portal with role selection (`Admin` / `Analyst`).
- **What to Explain**: OAuth2 JWT Bearer token authentication and bcrypt password hashing.
- **Evidence Proving Feature Works**: Form validates input and authenticates against database.

### Screen 2: Dashboard (`/dashboard`)
- **What to Show**: Key Metric Cards (Total Alerts, Critical/High/Med/Low counts, Average Risk Score, MTTD, MTTR, ML Anomalies).
- **What to Explain**: Real-time aggregation of active SIEM telemetry from database tables.
- **Evidence Proving Feature Works**: Metric values update dynamically when security events are ingested.

### Screen 3: Live Event Logs (`/logs`)
- **What to Show**: Ingested log table with timestamp, source IP, event type, severity, and ML Anomaly Score badges.
- **What to Explain**: Real-time log ingestion pipeline (`POST /api/v1/logs/`) and 10 tabular feature extraction.
- **Evidence Proving Feature Works**: Displays Isolation Forest predictions (`ANOMALOUS` / `NORMAL`) and model version (`IsolationForest-v1.2`).

### Screen 4: SIEM Alerts Queue (`/alerts`)
- **What to Show**: Priority badges (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), Detection Source tags (`RULE_BASED`, `ML_ANOMALY`, `HYBRID`), and Correlation ID badges.
- **What to Explain**: Transparent multi-factor risk scoring engine (0–100 scale).
- **Evidence Proving Feature Works**: Clicking the Info icon opens the itemized **Risk Breakdown** drawer showing exact factor point contributions.

### Screen 5: Correlation Chains (`/incidents`)
- **What to Show**: Multi-stage correlation chain cards with `CORR-YYYYMMDD-XXXX` IDs and stage progression stepper.
- **What to Explain**: 30-minute sliding window entity matching (`source_ip`, `user_name`, `hostname`).
- **Evidence Proving Feature Works**: Chronological attack timeline displays multi-step progression (Auth Fail $\rightarrow$ Auth Success $\rightarrow$ Priv Esc $\rightarrow$ Execution).

### Screen 6: Threat Intelligence (`/threat-intel`)
- **What to Show**: Known malicious IOC database (IPs, domains, file hashes) with threat scores.
- **What to Explain**: Local IOC matching enriches risk scores (+20 pts).
- **Evidence Proving Feature Works**: Searching IOC value returns threat status and associated alerts.

### Screen 7: AI Security Copilot (`/copilot`)
- **What to Show**: Chat UI rendering formatted 10-point analysis, Empirical Evidence Box, and Uncertainty Warning Box.
- **What to Explain**: Grounded evidence framework separating `FACT`, `INFERENCE`, `RECOMMENDATION`, and `UNCERTAINTY` with prompt injection defense.
- **Evidence Proving Feature Works**: Copilot output cites real log telemetry from DB without fabricating IPs or scores.

### Screen 8: Incident Response (`/incidents`)
- **What to Show**: Triage ticket controls, status updates (`NEW` $\rightarrow$ `INVESTIGATING` $\rightarrow$ `RESOLVED`), and analyst feedback buttons (`TRUE_POSITIVE`, `FALSE_POSITIVE`).
- **What to Explain**: Human-in-the-loop analyst feedback logging in `analyst_feedback` table.
- **Evidence Proving Feature Works**: Status updates persist in database and update UI immediately.

### Screen 9: Analytics Summary (`/analytics`)
- **What to Show**: Dynamic charts showing detection source distribution (`RULE_BASED` vs `ML_ANOMALY` vs `HYBRID`) and MTTD/MTTR metrics.
- **What to Explain**: Real-time SOC performance measurement.
- **Evidence Proving Feature Works**: Metrics calculated from actual database timestamps.

### Screen 10: Quantitative Benchmark Evaluation (`/analytics`)
- **What to Show**: Baseline vs AI/ML Detection comparison table and **Run Quantitative Benchmark Evaluation** button.
- **What to Explain**: Quantitative benchmarking on UNSW-NB15 dataset (70/15/15 split) showing **94.2% Precision** and **3.8% FPR**.
- **Evidence Proving Feature Works**: Clicking the button executes `SecurityEvaluationPipeline` and updates benchmark records.
