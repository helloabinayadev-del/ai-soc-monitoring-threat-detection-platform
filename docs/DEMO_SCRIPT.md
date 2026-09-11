# 10-Minute SOC Analyst Demonstration Script

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Step-by-Step Live Demonstration Walkthrough for Technical Presentations  

---

## Demonstration Overview (10 Minutes)

| Time | Demonstration Step | Target Endpoint / UI Component | Action & Narrative |
|---|---|---|---|
| **0:00 - 1:00** | **1. Login & Dashboard Overview** | `http://localhost:5173` | Login as `admin` (`Admin@123`). Show live telemetry stream, real-time WebSocket status badge (`CONNECTED`), and total alert counts. |
| **1:00 - 2:30** | **2. Telemetry Ingestion & Real-Time Alert**| `/api/v1/logs/simulate-scenario` | Trigger brute-force scenario (`brute_force`). Show real-time WebSocket alert pop-up with risk score 90.0 and `HYBRID` detection source. |
| **2:30 - 3:30** | **3. ML Anomaly & Feature Attribution** | `/api/v1/ml/predictions/{id}` | Inspect Isolation Forest anomaly score (85.2/100) and z-score feature attributions explaining top deviations. |
| **3:30 - 4:30** | **4. IOC Enrichment & ATT&CK Chain** | `/api/v1/mitre/attack-chain` | Enrich IP `198.51.100.45` via Threat Intel engine (`MALICIOUS`) and show ATT&CK Enterprise v14.1 tactical progression (`Credential Access` $\rightarrow$ `C2`). |
| **4:30 - 5:30** | **5. Proactive Threat Hunting** | `/api/v1/rules/hunting/query` | Demonstrate safe read-only search (`event_type=Authentication`, `search=failed login`) and natural language translation. |
| **5:30 - 7:00** | **6. Case Management & SHA-256 Hashes**| `POST /api/v1/incidents/1/evidence` | Attach raw log evidence to Case `INC-A1B2C3`. Point out the computed 64-character SHA-256 cryptographic hash. |
| **7:00 - 8:30** | **7. Grounded AI Copilot & SOAR Execution**| `/api/v1/playbooks/execute` | Show AI Copilot 10-point analysis referencing event IDs. Execute EDR host isolation playbook with `PENDING_APPROVAL` workflow. |
| **8:30 - 9:30** | **8. Forensic Case Report Export** | `GET /api/v1/incidents/1/report` | Export JSON forensic case report displaying `sha256_report_hash` and clear section headers (`ANALYST FINDINGS` vs `AI-GENERATED CONTENT`). |
| **9:30 - 10:00**| **9. Observability & Summary** | `GET /api/v1/health/detailed` | Show platform health diagnostics dashboard and conclude demonstration. |
