# Platform Capabilities & Technical Limitations Classification

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Truth-Mode Capability Matrix, Simulation Boundaries, & Real-World Limitations  

---

## 1. Truth-Mode Capability Classification Matrix

| Capability / Module | Truth-Mode Classification | Technical Rationale & Limitations |
|---|---|---|
| **Log Ingestion & Normalization** | **REAL IMPLEMENTATION** | Live FastAPI endpoint normalizes JSON log telemetry into database records. |
| **Isolation Forest ML Anomaly**| **REAL IMPLEMENTATION** | Scikit-Learn Isolation Forest model trained on 1,000 UNSW-NB15 benchmark logs. |
| **Signature Rule Engine** | **REAL IMPLEMENTATION** | Safe string/numerical condition evaluation without Python `eval()`. |
| **Risk Scoring & Correlation** | **REAL IMPLEMENTATION** | Multi-factor risk formula + entity pivot correlation engine. |
| **WebSocket Real-Time Stream** | **NEAR REAL-TIME** | ASGI WebSocket stream broadcasting sanitized event envelopes. |
| **Threat Intelligence Engine** | **REAL / LOCAL CACHE** | Local threat DB cache + configurable AbuseIPDB external API. |
| **MITRE ATT&CK Mapping** | **REAL IMPLEMENTATION** | Aligned with MITRE ATT&CK Enterprise v14.1 taxonomy. |
| **SOAR Containment Actions** | **LAB SIMULATION** | Outputs `SIMULATED ACTION: Would block IP x.x.x.x` without modifying host firewalls. |
| **Evidence SHA-256 Hashes** | **REAL IMPLEMENTATION** | Computes 64-character SHA-256 checksums per raw evidence payload. |
| **Quantitative Evaluation** | **CONTROLLED BENCHMARK** | Evaluates 70% Train / 15% Val / 15% Test split on UNSW-NB15 dataset. |
