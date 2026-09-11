# Detection Engineering Audit Report

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Audit Scope**: Signature Rules Engine, Rule Execution, & Detection Architecture  
**Date**: August 27, 2026  

---

## 1. Existing Rule Architecture Audit

| Subsystem Component | Implementation Location | Execution Rationale | Status |
|---|---|---|---|
| **Signature Rule Engine** | `app/ai/threat_classifier.py` | Keyphrase & condition matching against log `raw_message`. | **ACTIVE** |
| **Default MITRE ATT&CK Rules** | `RULE-001` through `RULE-007` | Signature patterns covering Brute Force, Priv Esc, PowerShell, C2, Exfil, SQLi, Ransomware. | **ACTIVE** |
| **Detection Source Classification**| `app/api/v1/endpoints/logs.py` | Categorizes alerts as `RULE_BASED`, `ML_ANOMALY`, or `HYBRID`. | **ACTIVE** |
| **Risk Score Contribution** | `prioritization_service.py` | Signature rule matches contribute +40.0 to +46.0 pts to risk score. | **ACTIVE** |
| **Correlation Integration** | `correlation_engine.py` | Rule-generated alerts enter the 30-minute sliding window entity matcher. | **ACTIVE** |
| **Rule Management API** | `app/api/v1/endpoints/rules.py` | REST API supporting CRUD, validation, testing, and lifecycle state transitions (`ACTIVE`, `DISABLED`, `DRAFT`, `DEPRECATED`). | **ACTIVE** |

---

## 2. Default Detection Rules

1. `RULE-001`: Multiple Failed Logins (Brute Force) — `HIGH` (75.0)
2. `RULE-002`: Privilege Escalation via Sudo/Admin — `CRITICAL` (90.0)
3. `RULE-003`: Suspicious PowerShell Command Execution — `HIGH` (85.0)
4. `RULE-004`: Outbound Connection to Known Malicious C2 — `CRITICAL` (95.0)
5. `RULE-005`: Potential Data Exfiltration over Encrypted Tunnel — `HIGH` (80.0)
6. `RULE-006`: SQL Injection (SQLi) Web Application Attack — `CRITICAL` (92.0)
7. `RULE-007`: Ransomware / Malware File Encryption Activity — `CRITICAL` (98.0)
