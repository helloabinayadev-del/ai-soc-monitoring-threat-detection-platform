# Upgrade 1 — Real ML Anomaly Detection Implementation Report

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Upgrade Focus**: UPGRADE 1 — REAL ML ANOMALY DETECTION  
**Completion Date**: August 27, 2026  

---

## 1. Existing ML Capability (Before Upgrade)
- Prior to this upgrade, anomaly detection relied on a basic 4-feature prototype script (`src_port`, `dst_port`, `msg_len`, `action_factor`) returning basic heuristic scores.
- There was no persistent storage for ML predictions, no configurable threshold API, no modular feature extraction package, and no transparent feature attribution explanations.

---

## 2. Changes Made
- Created a modular ML architecture in `backend/app/ml/` (`feature_engineering.py`, `preprocessing.py`, `anomaly_detector.py`, `model_manager.py`, `evaluation_pipeline.py`).
- Implemented a Scikit-Learn `IsolationForest` anomaly detection engine fitted on baseline security log metrics.
- Built a 10-feature security metric extractor deriving tabular indicators strictly from existing log fields.
- Implemented z-score feature attribution to explain top contributing feature deviations for anomalous events.
- Created `MLPrediction` database entity to persist all prediction records.
- Added `/api/v1/ml/analyze`, `/api/v1/ml/results`, `/api/v1/ml/status`, `/api/v1/ml/threshold` REST endpoints.
- Integrated ML predictions with the SIEM alert pipeline, tagging each alert with `Detection Source`: `RULE_BASED`, `ML_ANOMALY`, or `HYBRID`.
- Enhanced Frontend (Live Event Logs, SIEM Alerts, Dashboard, Copilot) to display real Anomaly Status, Anomaly Score, Model Version (`IsolationForest-v1.2`), and Detection Source.

---

## 3. Files Changed / Created

### New Files Created:
1. `backend/app/models/ml_prediction.py`: `MLPrediction` SQLAlchemy ORM entity.
2. `backend/app/ml/feature_engineering.py`: `SecurityFeatureExtractor` class (10 security features).
3. `backend/app/ml/preprocessing.py`: `LogPreprocessor` class (`StandardScaler`).
4. `backend/app/ml/anomaly_detector.py`: `IsolationForestAnomalyDetector` class.
5. `backend/app/ml/model_manager.py`: `ModelManager` class.
6. `backend/app/api/v1/endpoints/ml.py`: REST endpoints for ML model status, threshold, analyze, and results.
7. `backend/tests/test_ml_anomaly_detection.py`: Pytest suite specifically testing Upgrade 1.
8. `ML_IMPLEMENTATION_REPORT.md`: This documentation report.

### Existing Files Modified:
1. `backend/app/models/log.py`: Added `model_version` and `feature_vector` columns.
2. `backend/app/models/alert.py`: Added `detection_source`, `priority`, `risk_factors`, `anomaly_score` columns.
3. `backend/app/models/__init__.py`: Registered `MLPrediction` in exported models list.
4. `backend/app/ai/anomaly_detector.py`: Updated adapter to delegate to `ml_anomaly_detector` with full backward compatibility.
5. `backend/app/api/v1/endpoints/logs.py`: Integrated Isolation Forest prediction and `MLPrediction` persistence in `ingest_log`.
6. `backend/app/api/v1/router.py`: Registered `/ml` endpoints.
7. `frontend/src/types/index.ts`: Added `detection_source`, `anomaly_score`, `model_version` properties.
8. `frontend/src/components/AlertCard.tsx`: Rendered `Detection Source: ML`, `Detection Source: Rule`, `Detection Source: HYBRID`.
9. `frontend/src/pages/DashboardPage.tsx`: Rendered ML anomaly count metric card.

---

## 4. Features Used & Documentation

Extracted by `SecurityFeatureExtractor` (`app/ml/feature_engineering.py`):

| # | Feature Name | Source Log Field | Description |
|---|---|---|---|
| 1 | `event_frequency` | `source_ip` + window | Rolling count of events from same Source IP |
| 2 | `failed_login_count` | `action` + `raw_message` | Cumulative authentication failures from Source IP |
| 3 | `successful_login_count` | `action` + `raw_message` | Cumulative successful authentications |
| 4 | `source_port_norm` | `source_port` | Normalized Source Port (`port / 65535.0`) |
| 5 | `destination_port_norm` | `destination_port` | Normalized Destination Port (`port / 65535.0`) |
| 6 | `event_type_code` | `event_type` | Numerical encoding (Authentication=1, NetworkConnection=2, ProcessCreation=3, PrivilegeEscalation=4, System=5) |
| 7 | `severity_numeric` | `severity` | Numerical scale (INFORMATIONAL=1, LOW=2, MEDIUM=3, HIGH=4, CRITICAL=5) |
| 8 | `is_failed_auth` | `action` / `raw_message` | Binary flag (1.0 if action is `FAIL`/`DENY` or failure in message) |
| 9 | `time_hour_norm` | `timestamp` | Time of day normalized (`hour / 24.0`) |
| 10 | `payload_length_norm` | `raw_message` | Length of raw log message normalized (`min(1.0, len/1000)`) |

---

## 5. Model & Configuration
- **Model**: `sklearn.ensemble.IsolationForest`
- **Model Version**: `IsolationForest-v1.2`
- **Hyperparameters**:
  - `n_estimators`: 100
  - `contamination`: 0.05 (5%)
  - `random_state`: 42
  - `n_jobs`: -1
  - `threshold`: **65.0** (Configurable via `POST /api/v1/ml/threshold`)
- **Return Data Structure**:
  ```json
  {
    "anomaly_score": 88.5,
    "prediction": "ANOMALOUS",
    "model_version": "IsolationForest-v1.2",
    "threshold": 65.0,
    "prediction_timestamp": "2026-08-27T18:17:00Z",
    "contributing_features": [
      {
        "feature": "failed_login_count",
        "value": 5.0,
        "z_score": 3.42,
        "description": "Repeated authentication failures observed (5 failed attempts)"
      }
    ]
  }
  ```

---

## 6. API Changes
- `POST /api/v1/ml/analyze`: Analyzes raw log payload dictionary on-demand.
- `GET /api/v1/ml/results`: Fetches persisted prediction records from `ml_predictions` DB table.
- `GET /api/v1/ml/status`: Returns model hyperparameters, version, and training status.
- `POST /api/v1/ml/threshold`: Configures decision threshold (clamped 10.0 to 95.0).

---

## 7. Database Changes
Added table `ml_predictions`:
- `id` (Integer, PK)
- `event_id` (Integer, FK -> `log_events.id`)
- `model_version` (String, default="IsolationForest-v1.2")
- `anomaly_score` (Float)
- `prediction` (String: "NORMAL" / "ANOMALOUS")
- `threshold` (Float)
- `contributing_features` (JSON)
- `created_at` (DateTime)

---

## 8. SIEM Alert Integration
SIEM alerts clearly distinguish detection sources:
- `RULE_BASED`: Alert triggered solely by threat signature rules (`RULE-001` through `RULE-007`).
- `ML_ANOMALY`: Alert triggered solely by Isolation Forest anomaly score exceeding threshold.
- `HYBRID`: Alert triggered by both rule signature match AND ML anomaly score exceeding threshold.

---

## 9. Test Verification Results
All 25 unit and integration tests passed:
- `tests/test_ml_anomaly_detection.py`: **6/6 PASSED**
- `tests/test_all_endpoints.py`: **PASSED**
- `tests/test_siem_ai.py`: **PASSED**
- `tests/test_upgraded_pipeline.py`: **PASSED**

---

## 10. Truth Mode Status Classification
- **ML Model Implementation**: **MODEL IMPLEMENTED** (Scikit-learn `IsolationForest` pipeline active and verified).
- **Dataset Used**: Baseline normal security log telemetry combined with synthetic test data.
- **Feature Count**: 10 security features.
- **Known Limitations**:
  1. Unsupervised Isolation Forest relies on anomalies being statistical outliers. Low-and-slow stealthy logins spanning multiple days require expanding rolling historical windows.
  2. Egress TLS payloads are unencrypted at network level; network layer indicators supplement payload text length.
