# Upgrade 9 — Threat Hunting Audit & Query Engine Specification

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Safe Read-Only Query Engine, SQL Injection Defense, & AI Natural Language Translation  

---

## 1. Threat Hunting Subsystem Audit Matrix

| Subsystem Component | Implementation Location | Security / Validation Mechanism | Status |
|---|---|---|---|
| **Safe Query Engine** | `app/services/threat_hunting_engine.py` | Parameterized ORM queries only (no raw SQL `eval` or string concatenation) | **IMPLEMENTED** |
| **SQL Injection Defense** | `execute_safe_hunt` | Rejects SQL manipulation keywords (`DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER`, `;--`) | **IMPLEMENTED** |
| **Natural Language Translator**| `ai_natural_language_hunt` | Maps natural language prompts to safe ORM parameters | **IMPLEMENTED** |
| **Saved Hunts Engine** | `save_hunt` | Persists hunt queries with author, description, and query schema | **IMPLEMENTED** |
| **Backend Pagination** | `get_logs` / `execute_safe_hunt` | Enforces `skip` and `limit` capping max 50 events per page | **IMPLEMENTED** |

---

## 2. Supported Hunting Fields

- **Network Indicators**: `source_ip`, `destination_ip`
- **Identity Indicators**: `user_name`, `hostname`
- **Telemetry Categorization**: `event_type`, `severity`, `log_source`
- **Telemetry Anomaly Filter**: `is_anomaly`, `min_anomaly_score`
- **Text Search**: `search` (Full-text raw log substring match)
- **Time Range**: `time_range_hours` (Defaults to 24h, configurable)
