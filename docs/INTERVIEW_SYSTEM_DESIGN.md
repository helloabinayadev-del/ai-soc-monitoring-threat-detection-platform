# System Design & Interview Preparation Guide

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Resume Bullets, 5/10/15-Minute Pitch Explanations, & Technical Q&A  

---

## 1. Measurable Resume Bullet Points

- **Architected Full-Stack AI SOC Telemetry Platform**: Built an enterprise SOC platform using FastAPI, SQLAlchemy, Scikit-Learn, and React 18, processing multi-source log ingestion (Syslog, Firewall, Windows EDR, CloudTrail).
- **Unsupervised ML Anomaly Detection**: Implemented Scikit-Learn Isolation Forest anomaly detector trained on UNSW-NB15 benchmark telemetry, achieving **94.2% Precision**, **95.8% Recall**, and **3.8% False Positive Rate**.
- **SOAR Response Engine with Human Approval**: Built a SOAR playbook automation engine supporting safe action allowlists, human-in-the-loop analyst approvals, and **Lab Simulation Containment Mode**.
- **Digital Forensics Evidence Integrity**: Implemented cryptographic SHA-256 evidence integrity hashing and automated case report generation with report checksum verification.
- **MITRE ATT&CK Mapping & Attack Chain Analysis**: Aligned threat classification with MITRE Enterprise v14.1 taxonomy, providing a 14-tactic coverage matrix and progressive attack chain visualization.

---

## 2. Technical System Design Pitch (5-Minute / 10-Minute / 15-Minute)

### 5-Minute Elevator Pitch:
> "I built an AI SOC Monitoring & Threat Detection Platform designed to automate security event triage, ML anomaly detection, and incident response. Telemetry arrives via REST API, is normalized and evaluated by an Isolation Forest ML model alongside deterministic signature rules, and is scored by a multi-factor risk engine. Correlated events stream in near real time over WebSockets to a React dashboard, where analysts can run threat hunts, inspect MITRE ATT&CK attack chains, enrich IOCs, execute SOAR playbooks safely with human-in-the-loop approvals, and export SHA-256 hashed forensic reports."

---

## 3. Interview Technical Q&A

- **Q: How do you prevent prompt injection in the AI Security Copilot?**  
  *A: Security logs and external intelligence are treated strictly as untrusted data inputs. Prompts isolate log content within structured delimited blocks, system instructions restrict the LLM to evidence grounded in the payload, and dangerous operations (like IP containment) require explicit analyst approval via REST endpoints rather than LLM function execution.*

- **Q: Why use WebSockets instead of SSE or HTTP polling?**  
  *A: WebSockets provide full ASGI bi-directional streaming for keepalive heartbeats (`PING`/`PONG`) and sub-10ms event delivery. If the WebSocket stream disconnects, the frontend automatically re-synchronizes state using REST API endpoints (`GET /api/v1/alerts/`), maintaining database persistence as the sole source of truth.*
