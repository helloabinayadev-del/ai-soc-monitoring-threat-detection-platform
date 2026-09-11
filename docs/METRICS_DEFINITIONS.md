# SOC Observability & Operational Intelligence Metric Definitions

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Operational Platform Health, Subsystem Telemetry, & Metric Formulations  

---

## 1. Subsystem Health & Diagnostics KPIs

| Observability Component | Metric Name | Data Source | Calculation Formula / Meaning |
|---|---|---|---|
| **System Health** | Subsystem Status | `GET /api/v1/health/` | Evaluates live database, ML engine, and WebSocket connections (`HEALTHY` / `DEGRADED`). |
| **Log Ingestion** | Ingestion Volume | `log_events` table | Total count of raw logs ingested and normalized per hour/day. |
| **Detection Engine** | Rule Match Frequency | `security_alerts` table | Distribution of rule triggers across active signature rules (`RULE-001` to `RULE-006`). |
| **ML Anomaly Detection** | Anomaly Detection Ratio | `ml_predictions` table | Proportion of ingested logs classified as `ANOMALOUS` vs `NORMAL`. |
| **Risk Prioritization** | Critical Alert Ratio | `security_alerts` table | Percentage of SIEM alerts assigned `CRITICAL` or `HIGH` priority scores ($\ge 75.0$). |
| **Event Correlation** | Compression Ratio | `correlation_groups` | $\frac{\text{Total Events} - \text{Correlated Groups}}{\text{Total Events}} \times 100\%$. |
| **SOAR Automation** | Execution Success Rate | `playbook_engine` | $\frac{\text{Completed Executions}}{\text{Total Executed Playbooks}} \times 100\%$. |
| **Real-Time Stream** | Active Connections | `ws_manager` | Count of concurrent active WebSocket client connections. |
