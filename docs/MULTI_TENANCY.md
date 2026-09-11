# Multi-Tenant Architecture & Data Isolation Specification

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Single-User to Multi-Tenant Conversion, Data Models, RBAC, & IDOR Defense  
**Date**: August 28, 2026  

---

## 1. Multi-Tenant Logical Data Model Flow

```
[ User Account ]
       ↓
[ OrganizationMember Association (Role: OrgAdmin, Analyst, Viewer) ]
       ↓
[ Organization Tenant Boundary (Organization ID) ]
       ↓
┌─────────────────────────────────────────────────────────────┐
│                    Tenant-Isolated Data                     │
│  - Log Events (log_events.organization_id)                  │
│  - Security Alerts (security_alerts.organization_id)        │
│  - Incident Cases (incidents.organization_id)               │
│  - Correlation Groups (correlation_groups.organization_id) │
│  - Audit Trail Logs (audit_logs.organization_id)            │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Tenant Isolation & IDOR Defense Controls

1. **Server-Side Enforcement**:
   - Tenant boundaries are strictly enforced in backend Python ORM queries (`Model.organization_id == current_org_id`). Frontend role or tenant states are never trusted for authorization.

2. **IDOR Protection**:
   - Querying a case (`GET /api/v1/incidents/{id}`) or alert belonging to another organization yields HTTP `404 Not Found`, preventing cross-tenant enumeration.

3. **Backward Compatibility**:
   - Single-user deployments automatically initialize `Default Organization` (`org_id=1`), preserving existing database records and single-user workflows without data loss.
