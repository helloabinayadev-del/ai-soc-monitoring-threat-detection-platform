# API.md - AI SOC Monitoring Platform API Specification

Interactive OpenAPI Swagger UI is accessible at `/docs` when the backend server is running.

## Endpoint Summary

### System Health
- `GET /api/v1/health/`: Returns real dependency health check (Database connection, ML engine fitted status, Threat Intel count).

### Authentication & Users
- `POST /api/v1/auth/token`: Issues JWT bearer access token given valid `username` & `password`.
- `POST /api/v1/auth/register`: Registers a new user.
- `GET /api/v1/auth/me`: Retrieves current authenticated user profile.

### Log Ingestion & Query
- `POST /api/v1/logs/`: Ingests raw security log event, runs IsolationForest anomaly detection, evaluates SIEM correlation rules, and returns normalized LogEvent.
- `GET /api/v1/logs/`: Queries security event logs with filtering by `source`, `severity`, `anomaly_only`, and keyword `search`.

### SIEM Security Alerts
- `GET /api/v1/alerts/`: Retrieves security alerts with optional `severity` and `status` filters.
- `GET /api/v1/alerts/{alert_id}`: Retrieves single alert details.
- `PATCH /api/v1/alerts/{alert_id}/status`: Updates alert status (`NEW`, `INVESTIGATING`, `IN_PROGRESS`, `RESOLVED`, `FALSE_POSITIVE`).

### Incident Response
- `POST /api/v1/incidents/`: Creates incident response ticket with assigned systems and MITRE tactics.
- `GET /api/v1/incidents/`: Queries active incident tickets.
- `PUT /api/v1/incidents/{incident_id}/assign`: Assigns SOC analyst to incident ticket.
- `POST /api/v1/incidents/{incident_id}/containment-action`: Executes simulated SOAR containment action (`ISOLATE_HOST`, `BLOCK_IP`, `REVOKE_TOKENS`, `EDR_FULL_SCAN`).

### Threat Intelligence & CVE Lookup
- `GET /api/v1/intelligence/`: Returns list of threat intelligence indicators (IOCs).
- `POST /api/v1/intelligence/`: Adds new IOC to threat database.
- `GET /api/v1/intelligence/lookup/{ioc_value}`: Queries IP, hash, or domain against threat database.
- `GET /api/v1/intelligence/cve/{cve_id}`: Looks up CVE record details and CVSS scores from NVD database.

### AI Security Copilot
- `POST /api/v1/copilot/query`: Analyzes query and security context to return threat synthesis, action items, and MITRE references.

### Analytics Summary
- `GET /api/v1/analytics/summary`: Returns aggregate metric counts, severity distribution map, category breakdown, and overall SOC threat level.
