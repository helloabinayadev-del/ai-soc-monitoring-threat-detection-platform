# Database Schema & Data Flow Specification

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Relational Database Schema & Data Flow Design  

---

## 1. Relational Database Schema & Entity Models

The platform uses SQLAlchemy ORM mapping to SQLite (`soc_platform.db`), fully compatible with PostgreSQL.

```
┌─────────────────────────────────┐
│            users                │
├─────────────────────────────────┤
│ PK  id           Integer        │
│     username     String (Unique)│
│     hashed_pass  String         │
│     role         String         │
│     created_at   DateTime       │
└─────────────────────────────────┘

┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│          log_events             │       │         ml_predictions          │
├─────────────────────────────────┤       ├─────────────────────────────────┤
│ PK  id           Integer        │◄──────┤ PK  id           Integer        │
│     timestamp    DateTime (Idx) │       │ FK  event_id     Integer (Idx)  │
│     log_source   String         │       │     model_ver    String         │
│     event_type   String         │       │     anomaly_score Float         │
│     source_ip    String (Idx)   │       │     prediction   String         │
│     dest_ip      String         │       │     threshold    Float          │
│     source_port  Integer        │       │     contrib_feat JSON           │
│     dest_port    Integer        │       │     created_at   DateTime       │
│     user_name    String         │       └─────────────────────────────────┘
│     hostname     String         │
│     action       String         │
│     severity     String         │
│     raw_message  Text           │
│     anomaly_score Float         │
│     is_anomaly   String         │
│     model_ver    String         │
│     correlation_id String (Idx) │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│         security_alerts         │       │       correlation_groups        │
├─────────────────────────────────┤       ├─────────────────────────────────┤
│ PK  id           Integer        │       │ PK  id           Integer        │
│     title        String         │       │     correlation_id String(Idx)  │
│     description  Text           │       │     pattern_name String         │
│     rule_id      String         │       │     primary_entity String       │
│     severity     String         │       │     entity_value String         │
│     category     String         │       │     event_count  Integer        │
│     risk_score   Float          │       │     max_risk_score Float        │
│     priority     String (Idx)   │◄──────┤     status       String         │
│     detect_source String (Idx)  │       │     first_seen   DateTime       │
│     risk_factors JSON           │       │     last_seen    DateTime       │
│     anomaly_score Float         │       └─────────────────────────────────┘
│ FK  correlation_id String(Idx)  │
│     source_event_ids JSON       │
│     created_at   DateTime       │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│           incidents             │       │        analyst_feedback         │
├─────────────────────────────────┤       ├─────────────────────────────────┤
│ PK  id           Integer        │       │ PK  id           Integer        │
│     title        String         │       │ FK  alert_id     Integer (Idx)  │
│     description  Text           │       │     label        String         │
│     severity     String         │       │     analyst_user String         │
│     status       String         │       │     notes        Text           │
│     assignee     String         │       │     created_at   DateTime       │
│ FK  correlation_id String(Idx)  │       └─────────────────────────────────┘
└─────────────────────────────────┘
```

---

## 2. Table Indexing & Performance Strategy

- **`log_events` Indexes**: `timestamp`, `source_ip`, `correlation_id` (Optimizes sliding time-window queries).
- **`security_alerts` Indexes**: `priority`, `detection_source`, `correlation_id`, `created_at` (Optimizes alert queue sorting and priority filtering).
- **`correlation_groups` Indexes**: `correlation_id`, `status` (Optimizes incident correlation linking).
- **`ml_predictions` Indexes**: `event_id`, `created_at` (Optimizes ML prediction lookup per ingested event).

---

## 3. Data Flow Architecture

```
1. Raw Log Ingestion
   -> LogEvent record saved in log_events table.
2. ML Anomaly Prediction
   -> Isolation Forest score computed.
   -> MLPrediction record saved in ml_predictions table.
3. Event Correlation
   -> Entity matching in 30-min window.
   -> CorrelationGroup created/updated in correlation_groups table with ID CORR-YYYYMMDD-XXXX.
4. Risk Prioritization
   -> Risk score computed.
   -> SecurityAlert record saved in security_alerts table with priority and risk_factors.
5. Copilot Analysis
   -> Queries log_events, security_alerts, ml_predictions, and correlation_groups for 10-point grounded analysis.
6. Incident Response & Feedback
   -> Analyst feedback stored in analyst_feedback table.
```
