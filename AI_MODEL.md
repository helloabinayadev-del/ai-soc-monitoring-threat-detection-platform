# AI_MODEL.md - Scikit-Learn IsolationForest Anomaly Detection Model

## Overview

The AI Anomaly Detection module (`app/ai/anomaly_detector.py`) uses an unsupervised **IsolationForest** machine learning algorithm implemented via `scikit-learn`.

## Architecture & Algorithm

- **Model Class**: `sklearn.ensemble.IsolationForest`
- **Hyperparameters**:
  - `n_estimators`: 100 decision trees
  - `contamination`: 0.05 (5% target contamination threshold)
  - `random_state`: 42 (reproducible seed)

## Feature Engineering

Each ingested security event log is preprocessed into a 4-dimensional numerical feature vector:

1. `source_port`: Numerical source port (default: 80).
2. `destination_port`: Numerical destination port (default: 443).
3. `msg_len`: Length of the raw log string message.
4. `action_factor`: Weighted multiplier based on security execution state (`500.0` for `DENY`/`FAIL`/`EXECUTE`, `50.0` for `ALLOW`).

## Anomaly Score Normalization

Isolation Forest outputs raw decision scores (typically between -0.5 and +0.5).
The model normalizes decision values onto a **0.0 to 100.0** risk score scale:

$$\text{Normalized Score} = \max\left(0.0, \min\left(100.0, \text{round}((0.5 - \text{raw\_score}) \times 100, 2)\right)\right)$$

- **Normal Classification**: Score $\le 65.0$
- **Anomalous Classification**: Score $> 65.0$ (triggers automatic high-priority SIEM security alert)

## Limitations & Edge Cases

- **Cold Start**: Pre-fitted on synthetic normal network log distributions during initialization.
- **Unsupervised Learning**: Operates purely on statistical outliers. SIEM rule correlation complements ML anomaly scoring to reduce false positives.
