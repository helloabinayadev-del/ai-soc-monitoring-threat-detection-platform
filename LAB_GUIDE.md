# REAL SOC LAB MODE — OPERATIONAL RUNBOOK & GUIDE

Welcome to the **AI SOC Monitoring & Threat Detection Platform** local SOC Lab! This platform enables security analysts to generate safe synthetic security events, trigger automated SIEM detection rules, investigate indicators of compromise (IOCs), converse with the AI Security Copilot, manage incident response workflows, and track real-time security analytics.

---

## 1. Environment Setup & Launch Commands

### Prerequisites
- **Python**: 3.10+ (Dependencies: `fastapi`, `uvicorn`, `sqlalchemy`, `passlib`, `python-jose`, `scikit-learn`)
- **Node.js**: v18+ / npm

### Step 1: Start the Backend API Server
From the root directory:
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **Backend API Base**: `http://localhost:8000/api/v1`
- **Swagger Interactive API Documentation**: `http://localhost:8000/docs`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

### Step 2: Start the Frontend React Console
From the root directory:
```bash
cd frontend
npm run dev
```
- **SOC Web App**: `http://localhost:5173`

---

## 2. Authentication & Access Credentials

- **Username**: `admin`
- **Password**: `Admin@123`
- **Role**: `Admin` (Full SOC Lead Administrator access)

Login endpoint: `POST /api/v1/auth/token` (Form Data: `username`, `password`)

---

## 3. End-to-End SOC Lab Analyst Workflow

### Phase A: Generating Synthetic Security Events
You can generate synthetic security events via **3 methods**:

#### Method 1: One-Click UI Scenario Control (Recommended)
1. Open the **Security Event Log Explorer** (`/logs`).
2. Use the **Lab Event Scenario** dropdown menu in the top action bar:
   - `Lab Event: Brute Force Login`
   - `Lab Event: Sudo Privilege Escalation`
   - `Lab Event: PowerShell Stager`
   - `Lab Event: Outbound C2 Beacon`
   - `Lab Event: SQL Injection Attack`
3. Click **Run Scenario**. The log event is ingested and processed immediately.

#### Method 2: Custom Log Ingestion Modal
1. On the `/logs` page, click **Custom Log**.
2. Fill in Log Source (`WindowsEvent`, `LinuxSyslog`, `EndpointEDR`, `Firewall`), Event Type, and Raw Log Message.
3. Click **Submit Log**.

#### Method 3: Direct API Ingestion (Swagger / Curl)
- **Endpoint**: `POST http://localhost:8000/api/v1/logs/`
- **JSON Payload Example**:
```json
{
  "log_source": "WindowsEvent",
  "event_type": "Authentication",
  "source_ip": "192.168.1.105",
  "destination_ip": "10.0.0.5",
  "user_name": "admin",
  "hostname": "WKSTN-FIN-02",
  "action": "FAIL",
  "severity": "HIGH",
  "raw_message": "EventID 4625: Account failed to log on. Invalid password attempt from 192.168.1.105 (failed login attempt)"
}
```

---

### Phase B: SIEM Detection Rule & Alert Correlation
When an event is ingested, the SIEM engine automatically runs rule evaluation:
- **Keyword Correlation Rules**:
  - `RULE-001`: Multiple Failed Logins (Brute Force) -> `HIGH` (Score: 75.0)
  - `RULE-002`: Privilege Escalation via Sudo/Admin -> `CRITICAL` (Score: 90.0)
  - `RULE-003`: Suspicious PowerShell Command Execution -> `HIGH` (Score: 85.0)
  - `RULE-004`: Outbound Connection to Known Malicious C2 -> `CRITICAL` (Score: 95.0)
  - `RULE-006`: SQL Injection (SQLi) Web Application Attack -> `CRITICAL` (Score: 92.0)

**Viewing Alerts**:
- Navigate to **SIEM Alerts** (`/alerts`).
- Newly correlated alerts appear with real-time risk scores, MITRE ATT&CK tactics, techniques, and affected assets.

---

### Phase C: Threat Intelligence Lookup
1. Navigate to **Threat Intelligence** (`/threat-intel`).
2. Input an IOC value in the **Real-Time Threat Intel Lookup** search box:
   - Malicious IP: `198.51.100.45` (Cobalt Strike C2 server)
   - MD5 Hash: `e3b0c44298fc1c149afbf4c8996fb924` (LockBit 3.0 Encryptor Payload)
   - CVE Lookup: `CVE-2021-44228` (Log4Shell Remote Code Execution)
3. Click **Lookup IOC**. If found in feeds, threat score and feed details are displayed. If not present, a clean "No matching IOC found" status is presented.

---

### Phase D: AI Security Copilot Investigation
1. Navigate to **AI Security Copilot** (`/copilot`) or click **Analyze with Copilot** on any alert card.
2. Ask natural language security questions:
   - *"Explain this alert and why it is suspicious."*
   - *"What are the recommended containment steps for Cobalt Strike C2 beaconing?"*
3. Copilot provides grounded technical summaries, MITRE references, confidence scores, and action items.

---

### Phase E: Incident Response & SOAR Containment Playbooks
1. Navigate to **Incident Response** (`/incidents`).
2. Click **New Incident Ticket** to create a ticket linked to the investigation.
3. Assign an analyst (`SOC Lead Administrator`) and set status (`IN_PROGRESS`).
4. Execute simulated SOAR containment playbook actions:
   - **Execute EDR Host Isolation**: Simulates network isolation of compromised workstation.
   - **Block Egress IP on Firewall**: Simulates boundary firewall rule creation.
   - **Revoke Active Directory Tokens**: Simulates session token revocation across domain.

---

### Phase F: Real-Time Analytics
1. Navigate to **Metrics & Analytics** (`/analytics`) or check the top banner threat indicator.
2. Verify that **Total Logs**, **Total Alerts**, **Critical Alerts**, and **Open Incidents** update dynamically based on actual database queries.

---

## 4. Distinguishing Seed Data vs. Lab-Generated Data

- **Seeded Demo Records**: Contain correlation IDs with `CORR-SEED-001` to `005` created during initial database setup.
- **Lab-Generated Records**: Contain auto-generated timestamps (`datetime.utcnow()`) and correlation IDs formatted as `CORR-YYYYMMDDHHMMSS-<N>`.

---

## 5. Security & Safety Rules

- **Lab Safety**: All simulated events use structured text logs. No malware binaries, real exploits, active scanning, or destructive shell execution take place.
- **Local Isolation**: The lab runs locally on `localhost`.
