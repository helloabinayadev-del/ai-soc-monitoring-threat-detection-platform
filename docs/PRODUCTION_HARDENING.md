# Production Hardening & Security Architecture Specification

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Security Controls, Error Masking, Secret Management, & Reliability  

---

## 1. Production Security Architecture

1. **Authentication & Token Expiration**:
   - Password hashing uses `passlib` with PBKDF2/Bcrypt algorithms.
   - JWT tokens signed with `JWT_SECRET` environment variable and enforced 60-minute expiration TTL.

2. **RBAC & Authorization Boundaries**:
   - `Admin`: Full access to create/update rules, execute playbooks, approve containment actions, update system settings.
   - `Analyst`: Access to view alerts, conduct threat hunting, execute safe playbooks, approve actions, and manage cases.
   - `Auditor`: Read-only access to view logs, audit trails, metrics, and evaluation reports.

3. **Safe Error Masking & Logging**:
   - Application errors log full technical stack traces to backend log files (`.system_generated/tasks/`), but return clean, non-revealing JSON error messages to clients (e.g. `{"detail": "Invalid request parameter"}`).
