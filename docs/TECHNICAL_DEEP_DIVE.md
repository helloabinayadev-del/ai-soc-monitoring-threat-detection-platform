# Technical Deep-Dive into Core Platform Engines

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Technical Implementation Deep-Dive (10 Core Engines)  

---

## 1. Log Ingestion Engine
- **Input**: Raw JSON security log payload via `POST /api/v1/logs/`.
- **Processing**: Pydantic schema validation (`LogEventCreate`), timestamp parsing, UTF-8 raw message sanitization.
- **Output**: Validated `LogEvent` dictionary.
- **Database**: Saved in `log_events` table.
- **API**: `POST /api/v1/logs/`.
- **Failure Handling**: HTTP 422 Unprocessable Entity returned for malformed JSON schemas.
- **Testing**: `tests/test_all_endpoints.py::test_ingest_log`.

---

## 2. Feature Extraction & Normalization Engine
- **Input**: `LogEvent` dictionary and recent 100-event history context.
- **Processing**: Extracts 10 tabular security metrics (`event_frequency`, `failed_login_count`, `successful_login_count`, `source_port_norm`, `destination_port_norm`, `event_type_code`, `severity_numeric`, `is_failed_auth`, `time_hour_norm`, `payload_length_norm`).
- **Output**: 1x10 NumPy feature vector (`float64`).
- **Database**: Saved in `feature_vector` column of `log_events`.
- **Testing**: `tests/test_ml_anomaly_detection.py::test_1_feature_extraction`.

---

## 3. SIEM Signature Detection Engine
- **Input**: Log `raw_message` and `parsed_fields`.
- **Processing**: Regex and string keyword matching against MITRE ATT&CK rules (`RULE-001` through `RULE-007`).
- **Output**: Matched rule object or `None`.
- **Testing**: `tests/test_siem_ai.py::test_threat_classifier`.

---

## 4. Scikit-Learn Isolation Forest ML Anomaly Engine
- **Input**: 1x10 Feature vector and baseline `StandardScaler`.
- **Processing**: `IsolationForest.decision_function()` computes raw anomaly score. Score is calibrated to 0–100 scale. Feature z-scores calculate transparent feature attributions.
- **Output**: `anomaly_score` (0–100), `prediction` (`ANOMALOUS` / `NORMAL`), `model_version` (`IsolationForest-v1.2`), `contributing_features`.
- **Database**: Saved in `ml_predictions` table.
- **API**: `POST /api/v1/ml/analyze`, `GET /api/v1/ml/status`, `POST /api/v1/ml/threshold`.
- **Testing**: `tests/test_ml_anomaly_detection.py::test_4_model_prediction_normal_vs_anomalous`.

---

## 5. Event Correlation Engine
- **Input**: New `LogEvent` and DB history within 30-minute sliding window.
- **Processing**: Matches shared entity keys (`source_ip`, `user_name`, `hostname`). Evaluates multi-stage attack sequences (Auth Failure $\rightarrow$ Success $\rightarrow$ Priv Esc $\rightarrow$ Execution).
- **Output**: `CorrelationGroup` object with ID `CORR-YYYYMMDD-XXXX`.
- **Database**: Saved in `correlation_groups` table.
- **API**: `GET /api/v1/correlations/`, `PATCH /api/v1/correlations/{id}/status`.
- **Testing**: `tests/test_upgraded_pipeline.py::test_e2e_upgraded_log_ingest_and_correlation`.

---

## 6. Transparent Multi-Factor Risk Scoring Engine
- **Input**: Severity, ML score, Rule match, Asset name, Threat Intel match, Correlation count.
- **Processing**:
  $$ \text{Risk Score} = \min\Big(100.0, \big(\text{Base Score} \times 0.50 + \text{ML Score} \times 0.50 + \text{Burst} + \text{TI} + \text{Corr}\big) \times \text{Asset Multiplier}\Big) $$
- **Output**: `risk_score` (0–100), `priority` (`LOW`/`MEDIUM`/`HIGH`/`CRITICAL`), `contributing_factors`.
- **Database**: Saved in `security_alerts` table.
- **Testing**: `tests/test_prioritization.py` (12 test scenarios).

---

## 7. Threat Intelligence IOC Matching Engine
- **Input**: `source_ip`, `destination_ip`, domain names.
- **Processing**: Matches indicators against `threat_intel` table records.
- **Output**: `threat_intel_match` (True/False) and threat score (+20 pts).
- **Database**: `threat_intel` table.
- **API**: `GET /api/v1/threat-intel/`.
- **Testing**: `tests/test_prioritization.py::test_7_threat_intelligence_match_contribution`.

---

## 8. Evidence-Based AI Security Copilot Engine
- **Input**: Query string and target `alert_id` / `correlation_id`.
- **Processing**: Queries database for empirical telemetry. Formats answer into 10-point framework separating `FACT`, `INFERENCE`, `RECOMMENDATION`, and `UNCERTAINTY`. Wraps untrusted log text in structural telemetry tags.
- **Output**: `CopilotResponse` Pydantic object.
- **API**: `POST /api/v1/copilot/query`.
- **Testing**: `tests/test_copilot.py` and `tests/test_siem_ai.py`.

---

## 9. Incident Triage & Feedback Engine
- **Input**: Alert ID, status update, analyst feedback label (`TRUE_POSITIVE`, `FALSE_POSITIVE`, `BENIGN`).
- **Processing**: Updates `SecurityAlert.status` and saves `AnalystFeedback` record.
- **Output**: Updated alert & incident ticket objects.
- **Database**: Saved in `security_alerts` and `analyst_feedback` tables.
- **API**: `PATCH /api/v1/alerts/{id}/status`, `POST /api/v1/feedback/`.
- **Testing**: `tests/test_all_endpoints.py`.

---

## 10. Quantitative Benchmark Evaluation Engine
- **Input**: UNSW-NB15 dataset telemetry test split (N=500).
- **Processing**: Evaluates rule baseline vs. AI/ML pipeline. Calculates Confusion Matrix, Precision, Recall, F1, FPR, FNR, MTTD, MTTR.
- **Output**: `ModelEvaluationRecord` object.
- **Database**: Saved in `model_evaluations` table.
- **API**: `GET /api/v1/evaluation/latest`, `POST /api/v1/evaluation/run`.
- **Testing**: `tests/test_upgraded_pipeline.py::test_evaluation_pipeline_execution`.
