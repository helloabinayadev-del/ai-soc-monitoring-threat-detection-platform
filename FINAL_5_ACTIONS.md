# Top 5 Highest-Value Remaining Actions

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Prioritized Post-Audit Engineering Actions  

---

## 1. PostgreSQL Production Connection Pooling
- **Action**: Configure SQLAlchemy connection pool parameters (`pool_size=20`, `max_overflow=10`) for multi-worker production deployments.
- **Impact**: Eliminates SQLite database file concurrency locks during high EPS bursts (>1,000 EPS).
- **Difficulty**: Low (Configuration update).

---

## 2. Automated Feedback-Driven ML Retraining Loop
- **Action**: Implement a background worker job that automatically retrains the Isolation Forest model when accumulated analyst feedback exceeds 100 labeled instances.
- **Impact**: Automatically adapts feature scalers to analyst feedback (`TRUE_POSITIVE` vs `FALSE_POSITIVE`) without requiring manual administrative restarts.
- **Difficulty**: Medium (3–4 hours).

---

## 3. Time-Indexed Log Correlation History Queries
- **Action**: Replace fixed `.limit(100)` query filter in log ingestion (`logs.py`) with time-indexed 30-minute window filtering (`LogEvent.timestamp >= NOW - 30 MIN`).
- **Impact**: Ensures 100% complete event history context for correlation during high EPS bursts.
- **Difficulty**: Low (30 minutes).

---

## 4. External Slack / PagerDuty Webhook Notifications
- **Action**: Extend WebSocket notification dispatcher in `ws_manager` to support external webhook dispatchers for `CRITICAL` priority alerts.
- **Impact**: Delivers mobile alerts to analysts disconnected from the live web UI.
- **Difficulty**: Medium (2 hours).

---

## 5. Python 3.14 Standardized Datetime Callbacks
- **Action**: Replace legacy `datetime.utcnow()` calls across SQLAlchemy model defaults with Python 3.14 timezone-aware `datetime.now(timezone.utc)`.
- **Impact**: Eliminates Python 3.14 standard library deprecation warnings during automated test execution.
- **Difficulty**: Low (30 minutes).
