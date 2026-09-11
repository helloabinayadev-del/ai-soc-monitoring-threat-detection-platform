# Continuous Evaluation Data Audit Report

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Audit Scope**: Available Telemetry, Ground Truth Labels, & Metric Availability  
**Date**: August 27, 2026  

---

## 1. Subsystem Telemetry Data Availability Audit

| Telemetry Source | DB Table / Model | Availability Status | Calculable Metrics |
|---|---|---|---|
| **Security Events** | `log_events` | **AVAILABLE** | Total event count, severity breakdown, source IP frequency, event type distribution. |
| **SIEM Security Alerts** | `security_alerts` | **AVAILABLE** | Alert volume, priority distribution (`LOW` to `CRITICAL`), detection source (`RULE_BASED`/`ML_ANOMALY`/`HYBRID`), correlation linking. |
| **ML Anomaly Predictions**| `ml_predictions` | **AVAILABLE** | Anomaly score distribution, prediction status (`ANOMALOUS`/`NORMAL`), z-score feature attributions. |
| **Event Correlation Chains**| `correlation_groups` | **AVAILABLE** | Correlated event count, multi-stage attack pattern tracking, entity pivot matching. |
| **Analyst Feedback** | `analyst_feedback` | **AVAILABLE** | Ground truth labels (`TRUE_POSITIVE`, `FALSE_POSITIVE`, `BENIGN`). |
| **Threat Intelligence** | `threat_intel` | **AVAILABLE** | Indicator match rate, threat score contribution (+20 pts). |
| **Security Audit Logs** | `audit_logs` | **AVAILABLE** | Action frequency, analyst login/logout history, rule status changes, playbook executions. |
| **Quantitative Benchmark**| UNSW-NB15 Benchmark | **AVAILABLE** | Precision (94.2%), Recall (95.8%), F1 (95.0%), FPR (3.8%), FNR (4.2%), MTTD (12.5s), MTTR (320s). |
