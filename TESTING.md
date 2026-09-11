# TESTING.md - AI SOC Monitoring Platform Testing Strategy

## Test Suite Structure

The platform includes automated testing across both backend and frontend layers.

### 1. Backend Pytest Suite
Location: `backend/tests/`

- `test_auth.py`: Verifies root health endpoint, user registration, and JWT token authentication.
- `test_siem_ai.py`: Verifies IsolationForest anomaly model predictions, SIEM threat classifier rule evaluation, and AI Copilot query synthesis.

#### Execution Command
```bash
cd backend
python -m pytest tests
```

### 2. Frontend Type Checking & Vite Build Validation
Location: `frontend/`

- TypeScript compiler (`tsc`) verifies strict type safety across components, context providers, and API interfaces.
- Vite production build verifies asset bundling and CSS minification.

#### Execution Command
```bash
cd frontend
npm run build
```

## E2E Workflow Verification Matrix

| Workflow Step | Verified Endpoint / Component | Test Status |
|---|---|---|
| User Authentication | `POST /api/v1/auth/token` | PASSED |
| Log Ingestion & Normalization | `POST /api/v1/logs/` | PASSED |
| IsolationForest Anomaly Scoring | `LogAnomalyDetector.predict()` | PASSED |
| SIEM Correlation & Alert Trigger | `ThreatClassifier.classify_log()` | PASSED |
| Real-Time WebSocket Streaming | `/ws/soc-stream` | PASSED |
| Incident Ticket & SOAR Action | `POST /incidents/{id}/containment-action` | PASSED |
| Copilot Contextual Analysis | `POST /api/v1/copilot/query` | PASSED |
