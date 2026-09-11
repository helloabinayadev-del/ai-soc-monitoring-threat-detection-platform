# Phase A — Combined Upgrade System Audit Report

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Audit Scope**: Combined Upgrades 3 + 4 + 5 (Event Correlation + Explainable AI + Quantitative Evaluation)  
**Date**: August 27, 2026  

---

## 1. Current Security Event Structure
- **Table**: `log_events` (SQLAlchemy ORM model in `backend/app/models/log.py`)
- **Key Fields**:
  - `id`: Integer (Primary Key)
  - `timestamp`: DateTime (UTC)
  - `log_source`: String (`Firewall`, `WindowsEvent`, `LinuxSyslog`, `AWSCloudTrail`, `EndpointEDR`)
  - `event_type`: String (`Authentication`, `NetworkConnection`, `ProcessCreation`, `PrivilegeEscalation`)
  - `source_ip`: String
  - `destination_ip`: String
  - `source_port`: Integer
  - `destination_port`: Integer
  - `user_name`: String
  - `hostname`: String
  - `action`: String (`ALLOW`, `DENY`, `EXECUTE`, `FAIL`, `SUCCESS`)
  - `severity`: String (`INFORMATIONAL`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)
  - `raw_message`: Text
  - `parsed_fields`: JSON
  - `anomaly_score`: Float (0.0 to 100.0)
  - `is_anomaly`: String (`NORMAL`, `ANOMALOUS`)
  - `model_version`: String (`IsolationForest-v1.2`)
  - `feature_vector`: JSON
  - `correlation_id`: String (e.g. `CORR-20260827-0001`)

---

## 2. Current SIEM Alert Structure
- **Table**: `security_alerts` (SQLAlchemy ORM model in `backend/app/models/alert.py`)
- **Key Fields**:
  - `id`: Integer (Primary Key)
  - `title`: String
  - `description`: Text
  - `rule_id`: String (`RULE-001` through `RULE-007`, `ML-ANOMALY-001`)
  - `severity`: String (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)
  - `category`: String (`Initial Access`, `Credential Access`, `Execution`, `Privilege Escalation`, `Command and Control`)
  - `risk_score`: Float (0.0 to 100.0)
  - `priority`: String (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)
  - `detection_source`: String (`RULE_BASED`, `ML_ANOMALY`, `HYBRID`)
  - `risk_factors`: JSON (Array of itemized factor contributions)
  - `anomaly_score`: Float
  - `correlation_id`: String
  - `status`: String (`NEW`, `INVESTIGATING`, `CONFIRMED`, `DISMISSED`, `RESOLVED`)
  - `created_at`: DateTime (UTC)

---

## 3. Current ML Anomaly Detection Capability
- **Engine**: Scikit-Learn `IsolationForest` pipeline (`backend/app/ml/anomaly_detector.py`).
- **Feature Extractor**: 10 tabular security metrics (`event_frequency`, `failed_login_count`, `successful_login_count`, ports, severity, time-of-day, payload length).
- **Outputs**:
  - `anomaly_score`: Calibrated 0.0 to 100.0 scale.
  - `prediction`: `ANOMALOUS` (score > 65.0) or `NORMAL`.
  - `model_version`: `IsolationForest-v1.2`.
  - `contributing_features`: Feature z-score attributions explaining deviations.

---

## 4. Current Risk Scoring Capability
- **Engine**: `IntelligentAlertPrioritizationService` (`backend/app/services/prioritization_service.py`).
- **Multi-Factor Inputs**:
  - Base Severity / Rule Score (Weight 0.50)
  - Isolation Forest ML Anomaly Score (Weight 0.50)
  - Repeated Frequency Burst Points
  - Asset Criticality Multipliers (`DC-PRIMARY-01` = 1.30x)
  - Threat Intelligence Match (+20 pts)
  - Event Correlation Chain Strength (+6 pts/event)
  - Analyst Feedback Calibration (±15 pts)

---

## 5. Current Event Correlation Capability
- **Engine**: `EventCorrelationEngine` (`backend/app/services/correlation_engine.py`).
- **Sliding Time Window**: 30-minute sliding window entity matching (`source_ip`, `user_name`, `hostname`).
- **Correlation ID**: Unique `CORR-YYYYMMDD-XXXX` identifiers.
- **Pattern Tracking**: Tracks multi-stage attack progression (Credential Access -> Execution -> Privilege Escalation -> C2 Beacon).
- **Status Classification**: `OBSERVED`, `INVESTIGATING`, `CONFIRMED`, `DISMISSED`, `RESOLVED`.

---

## 6. Current AI Copilot Capability
- **Service**: `SecurityCopilotService` (`backend/app/services/copilot_service.py`).
- **Framework**: Grounded 10-point evidence framework.
- **Fact vs Inference**: Explicitly distinguishes `FACT`, `INFERENCE`, `RECOMMENDATION`, and `UNCERTAINTY`.
- **Prompt Injection Safeguard**: Sanitizes raw log messages as untrusted string telemetry.

---

## 7. Current Quantitative Evaluation Capability
- **Pipeline**: `SecurityEvaluationPipeline` (`backend/app/ml/evaluation_pipeline.py`).
- **Benchmark Data**: UNSW-NB15 dataset subsets with 70% Train / 15% Val / 15% Test splits.
- **Metrics Calculated**: Precision, Recall, F1 Score, False Positive Rate, False Negative Rate, MTTD, MTTR.

---

## 8. Database Relationships
```
[LogEvent] 1 --- * [MLPrediction]
   |
   +----------- * [SecurityAlert] (via source_event_ids / correlation_id)
                     |
                     +----------- 1 [CorrelationGroup] (via correlation_id)
                     |
                     +----------- * [AnalystFeedback] (via alert_id)
```

---

## 9. Existing REST APIs
- `/api/v1/logs/`: Ingestion & log listing.
- `/api/v1/alerts/`: Alert queue with priority, detection source, and min_risk_score filters.
- `/api/v1/ml/`: Model status, threshold updates, on-demand analysis, and prediction history.
- `/api/v1/correlations/`: Correlation chain listing, details, and status updates.
- `/api/v1/copilot/query`: Grounded 10-point AI Security Copilot query.
- `/api/v1/evaluation/`: Benchmark evaluation runner and latest metrics.
- `/api/v1/analytics/summary`: Analytics summary dashboard metrics.

---

## 10. Files Audit Table

| File Path | Role | Status |
|---|---|---|
| `backend/app/models/correlation.py` | ORM entity for Correlation Groups | Created & Verified |
| `backend/app/services/correlation_engine.py` | Event correlation logic | Created & Verified |
| `backend/app/api/v1/endpoints/correlations.py` | REST API for correlations | Created & Verified |
| `backend/app/services/copilot_service.py` | Evidence-grounded Copilot | Upgraded & Verified |
| `backend/app/ml/evaluation_pipeline.py` | Benchmark evaluation pipeline | Created & Verified |
| `backend/app/models/evaluation.py` | Evaluation & Feedback entities | Created & Verified |
| `frontend/src/pages/IncidentsPage.tsx` | UI for Correlation Chains | Upgraded & Verified |
| `frontend/src/components/CopilotChat.tsx` | UI for 10-point AI Copilot | Upgraded & Verified |
| `frontend/src/pages/AnalyticsPage.tsx` | UI for Model & SOC Evaluation | Upgraded & Verified |
