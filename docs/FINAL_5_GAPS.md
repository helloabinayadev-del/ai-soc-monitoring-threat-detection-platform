# Top 5 Remaining Technical Gaps & Proposed Fixes

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Prioritized Defect & Technical Improvement List  

---

## Gap 1: Database Concurrency Limits under High Multi-Worker Load (SQLite vs PostgreSQL)
- **Problem**: Default database connection string uses local SQLite file (`sqlite:///./soc_platform.db`).
- **Why It Matters**: Concurrent writes from multiple Uvicorn worker threads can hit `sqlite3.OperationalError: database is locked` during high EPS bursts.
- **Empirical Evidence**: `backend/app/core/database.py` line 7 defaults to SQLite.
- **Impact**: Medium (Affects high-concurrency multi-worker staging; zero impact on single-worker / development execution).
- **Proposed Fix**: Set `DATABASE_URL` environment variable to PostgreSQL with SQLAlchemy connection pooling (`pool_size=20`, `max_overflow=10`).
- **Estimated Difficulty**: Low (Configuration update).

---

## Gap 2: Lack of Automatic Retraining Loop for Analyst Feedback
- **Problem**: Analyst feedback (`TRUE_POSITIVE`, `FALSE_POSITIVE`, `BENIGN`) is persisted in DB, but does not automatically re-fit the Isolation Forest model.
- **Why It Matters**: The ML anomaly model relies on initial baseline training and requires explicit manual retraining calls.
- **Empirical Evidence**: `backend/app/models/evaluation.py` stores feedback labels, but `ml_anomaly_detector.fit()` is not hooked to a feedback threshold trigger.
- **Impact**: Low (Static model remains accurate for short-term evaluation; retraining loop is needed for multi-month drift mitigation).
- **Proposed Fix**: Add a background cron worker that triggers `model_manager.retrain()` when accumulated analyst feedback exceeds 100 labeled instances.
- **Estimated Difficulty**: Medium (3–4 hours).

---

## Gap 3: Fixed History Limit in Log Ingestion Correlation Queries
- **Problem**: Recent historical context queries in log ingestion fetch recent logs using `limit(100)`.
- **Why It Matters**: In high EPS log streams (>1,000 EPS), events occurring within 30 minutes might be skipped if >100 logs were ingested in between.
- **Empirical Evidence**: `backend/app/api/v1/endpoints/logs.py` line 26 specifies `.limit(100)`.
- **Impact**: Low (Affects high EPS burst environments).
- **Proposed Fix**: Replace `.limit(100)` with time-indexed query filter (`LogEvent.timestamp >= datetime.now(timezone.utc) - timedelta(minutes=30)`).
- **Estimated Difficulty**: Low (30 minutes).

---

## Gap 4: WebSocket-Only Real-Time Notification Dispatching
- **Problem**: Real-time notifications broadcast via WebSocket (`ws_manager`), but external webhook dispatchers (Slack, PagerDuty, Email) are mocked.
- **Why It Matters**: SOC analysts disconnected from the web dashboard will not receive external mobile alerts for `CRITICAL` priority events.
- **Empirical Evidence**: `backend/app/websockets/connection_manager.py` manages WebSocket connections without active SMTP/Webhook calls.
- **Impact**: Low (Dashboard notifications work for connected sessions).
- **Proposed Fix**: Implement an asynchronous webhook dispatcher module in `backend/app/services/notification_service.py`.
- **Estimated Difficulty**: Medium (2 hours).

---

## Gap 5: Legacy Standard Library Datetime Deprecation Warnings
- **Problem**: Pytest execution produces Python 3.14 deprecation warnings regarding `datetime.utcnow()`.
- **Why It Matters**: `datetime.utcnow()` is deprecated in Python 3.14 standard library.
- **Empirical Evidence**: Pytest warning output cites `DeprecationWarning: datetime.datetime.utcnow() is deprecated`.
- **Impact**: Low (Non-breaking warning).
- **Proposed Fix**: Replace all `datetime.utcnow()` calls across models with Python 3.14 timezone-aware `datetime.now(timezone.utc)`.
- **Estimated Difficulty**: Low (30 minutes).
