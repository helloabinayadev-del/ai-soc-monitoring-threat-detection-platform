# AI SOC Platform — Comprehensive Master Architecture Document

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Full Pipeline Architecture, Subsystem Integration, & Security Controls  

---

## 1. Master End-to-End SOC Workflow Architecture

```
[ Multi-Source Security Telemetry ]
                ↓
[ Ingestion & Field Normalization (/api/v1/logs/) ]
                ↓
[ Scikit-Learn Isolation Forest ML Anomaly Detection ]
                ↓
[ Signature Threat Classifier (Safe Condition Operators) ]
                ↓
[ Multi-Factor Intelligent Risk Engine (0.0 - 100.0) ]
                ↓
[ Event Correlation Engine (CORR-YYYYMMDD-XXXX) ]
                ↓
[ SIEM Alert Generation & Priority Scoring ]
                ↓
[ WebSocket Real-Time Event Streaming (/ws/soc-stream) ]
                ↓
[ Threat Intelligence & IOC Enrichment Engine ]
                ↓
[ MITRE ATT&CK Technique Mapping & Attack Chain Analysis ]
                ↓
[ Proactive Threat Hunting Workspace (Safe Read-Only Query Engine) ]
                ↓
[ Advanced Case Management & Digital Forensics (SHA-256 Hashes) ]
                ↓
[ Grounded AI Security Copilot Triage Assistant ]
                ↓
[ SOAR Response Playbook & Automation Engine (Analyst Approval) ]
                ↓
[ Security Audit Trail (audit_logs Table) ]
                ↓
[ Quantitative Evaluation Pipeline (UNSW-NB15 Benchmark Split) ]
                ↓
[ SOC Observability & System Diagnostics Dashboard ]
```

---

## 2. Core Subsystems Overview

1. **Backend Layer**: FastAPI ASGI framework with async WebSocket streaming and SQLAlchemy ORM layer.
2. **ML Anomaly Detection**: Unsupervised Isolation Forest model trained on normal background traffic ($y=0$), calculating anomaly scores and z-score feature attributions.
3. **SOAR Response Automation**: Safe action allowlist with human analyst approval workflows (`PENDING_APPROVAL`) and Lab Simulation Mode.
4. **Digital Forensics Integrity**: Cryptographic 256-bit SHA-256 hashes computed per raw evidence attachment and report artifact.
