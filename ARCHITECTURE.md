# ARCHITECTURE.md - AI SOC Monitoring Platform Architecture

## System Overview

The **AI SOC Monitoring & Threat Detection Platform** is built following Clean Architecture principles to provide an enterprise-grade security operations solution.

```
[ Security Event Producers ]
       │ (HTTP POST / Syslog / JSON)
       ▼
┌─────────────────────────────────────────────────────────────┐
│ FastApi Ingestion & Normalization Layer                     │
│  - ECS Schema Normalizer                                    │
│  - Correlation ID Generator                                 │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐
│ Scikit-Learn ML Engine      │ │ SIEM Rule Engine            │
│  - IsolationForest Model    │ │  - MITRE ATT&CK Rules       │
│  - Anomaly Scoring (0-100)   │ │  - Threat Classifier        │
└──────────────┬──────────────┘ └──────────────┬──────────────┘
               │                              │
               └──────────────┬───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Event Bus & Persistence Layer                               │
│  - SQLAlchemy 2.0 ORM (PostgreSQL / SQLite)                 │
│  - FastAPI WebSockets Broadcast (/ws/soc-stream)            │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐
│ AI Security Copilot Engine  │ │ Threat Intelligence Engine  │
│  - Contextual Analysis      │ │  - AlienVault OTX / Abuse   │
│  - Containment Playbooks    │ │  - NVD / CVE Database       │
└──────────────┬──────────────┘ └──────────────┬──────────────┘
               │                              │
               └──────────────┬───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ React 18 + Vite + Tailwind Security Analyst Console         │
│  - Executive SOC Dashboard & Infrastructure Map             │
│  - Live Log Stream Table & SIEM Alert Queue                 │
│  - Incident Response SOAR Simulation Controls               │
└─────────────────────────────────────────────────────────────┘
```

## Core Service Components

1. **Ingestion & Normalization Pipeline**: Converts incoming Syslog, Windows EventID, PaloAlto Firewall, and CloudTrail payloads into standardized Elastic Common Schema (ECS) events with UUID correlation IDs.
2. **Scikit-Learn IsolationForest Anomaly Engine**: Performs unsupervised feature extraction on port metrics, payload length, and execution action weights to detect zero-day anomalies.
3. **SIEM Correlation Engine**: Evaluates log events against rule signatures (Brute Force, Sudo Privilege Escalation, Encoded PowerShell, Outbound C2, SQL Injection, Ransomware).
4. **Threat Intelligence Service**: Provides IOC indicator matching and NVD CVE vulnerability records.
5. **FastAPI WebSocket Manager**: Streams real-time `NEW_LOG` and `NEW_ALERT` events asynchronously to all connected SOC analyst dashboards.
6. **SOAR Incident Workflow Engine**: Manages 8-stage incident lifecycles (`NEW` -> `TRIAGING` -> `INVESTIGATING` -> `CONTAINMENT` -> `ERADICATION` -> `RECOVERY` -> `RESOLVED` -> `CLOSED`) with simulated EDR and Firewall response triggers.
