# SECURITY.md - AI SOC Monitoring Platform Security Architecture

## 1. Authentication & Session Security
- **HMAC-SHA256 JWT Tokens**: Issued upon successful login (`POST /api/v1/auth/token`) with 24-hour expiration.
- **Bcrypt Password Hashing**: Passwords are hashed using `passlib` bcrypt algorithm with dynamic salt rounds.
- **Zero Frontend Secret Storage**: Secret keys and database credentials are held strictly in backend environment configuration (`.env`). The frontend settings dashboard displays operational health status only.

## 2. Role-Based Access Control (RBAC)
- **Admin**: Full administrative access to system parameters, user management, and incident workflow triage.
- **Analyst**: Access to event log explorer, alert triage, threat lookup, and AI Copilot.
- **Auditor**: Read-only access to analytics dashboards and audit logs.

## 3. Data Protection & Input Sanitization
- **SQL Injection Defenses**: All database queries are executed via SQLAlchemy ORM parameterized statements.
- **XSS & Output Encoding**: React JSX automatic HTML escaping prevents cross-site scripting attacks.
- **CORS Policies**: Explicit origin restrictions configured via FastAPI CORSMiddleware (`BACKEND_CORS_ORIGINS`).

## 4. SOAR Safe Execution Boundary
- **Simulated Response Actions**: All network isolation, firewall IP blocking, and account token revocation actions run under an explicit **[SIMULATED SOAR ACTION - APPROVAL MODE]** workflow to prevent unintended production network disruptions.
