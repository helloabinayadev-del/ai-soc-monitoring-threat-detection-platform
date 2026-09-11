# SOC LAB DEMO & INTERVIEW PREPARATION GUIDE

This document provides a **5-Minute Live Interview Demonstration Script** and technical architecture Q&A for explaining the AI SOC Monitoring Platform to software engineering interviewers.

---

## 5-Minute Live Interview Script

### Step 1: Authentication & Overview (30 Seconds)
- Open `http://localhost:5173`. Point out the single, centered glassmorphism login interface.
- Log in using `admin` / `Admin@123`. Show automatic redirect to the **SOC Dashboard**.
- Point out the UTC live clock, global threat level indicator (`ELEVATED`), and unread threat notification popover.

### Step 2: Ingesting a Real Threat Scenario (1 Minute)
- Navigate to **Live Event Logs** (`/logs`).
- Select `Lab Event: Brute Force Login` from the **Lab Event Scenario** control.
- Click **Run Scenario**. Explain: *"When I click this, a synthetic Windows Event 4625 log is posted via REST to `/api/v1/logs/`. The backend passes it through field normalization, runs IsolationForest anomaly detection, and evaluates SIEM keyword rules."*

### Step 3: SIEM Alert & MITRE Correlation (1 Minute)
- Navigate to **SIEM Alerts** (`/alerts`).
- Show the newly correlated alert: `[HIGH] Multiple Failed Logins (Brute Force) (Rule: RULE-001)`.
- Explain: *"The SIEM engine matched `RULE-001` (Credential Access / Brute Force), mapped it to MITRE technique T1110, calculated a risk score of 75.0, and broadcasted a WebSocket event to all connected analyst consoles."*

### Step 4: AI Security Copilot Investigation (1 Minute)
- Click **Analyze with Copilot** on the alert card.
- Explain: *"The AI Copilot fetches the exact database alert ID and context. Unlike static LLM wrappers, our service grounds its response directly in the DB payload, returning risk reasoning, confidence scores, and specific remediation steps."*

### Step 5: Incident Management & SOAR Containment Playbook (1.5 Minutes)
- Navigate to **Incident Response** (`/incidents`).
- Click **Execute EDR Host Isolation**.
- Show the SOAR containment response: `[SIMULATED SOAR ACTION SUCCESS]: Successfully executed EDR network isolation command for affected host.`
- Navigate to **Metrics & Analytics** (`/analytics`). Point out that total logs, alert counts, and open incident metrics are computed directly via real SQL database aggregation queries.

---

## Key Technical Questions & Answers for Interviews

### Q1: Why FastAPI over Django or Flask?
**Answer**: FastAPI provides native asynchronous I/O support via ASGI/uvicorn, making high-throughput WebSocket log streaming and non-blocking endpoint execution extremely fast. Pydantic v2 automatically generates OpenAPI schemas and enforces strict request/response data validation.

### Q2: How do you prevent AI hallucination in the Security Copilot?
**Answer**: We pass the exact database primary key (`context_alert_id`) into `copilot_service.py`. The backend queries `SecurityAlert` directly from the database and constructs the prompt using empirical telemetry (source IP, MITRE technique, rule ID, affected asset). If no matching alert ID exists, it explicitly responds with an "Insufficient Evidence" status.

### Q3: How is data persistence handled between development and production?
**Answer**: We use SQLAlchemy ORM abstraction. In development/local lab mode, SQLite (`soc_platform.db`) provides lightweight zero-config persistence. In production/Docker mode, setting `DATABASE_URL` seamlessly switches the application to PostgreSQL 15.

### Q4: How is Role-Based Access Control (RBAC) enforced?
**Answer**: We enforce authorization server-side using FastAPI dependency injection (`require_roles(["Admin", "SOC Lead"])`). Hiding UI buttons in React is for user experience, but the backend strictly blocks unauthorized requests with HTTP 403 Forbidden.
