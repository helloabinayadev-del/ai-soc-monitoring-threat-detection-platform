from fastapi import Depends, HTTPException, status
from typing import List, Callable
from app.models.user import User

ROLE_MAP = {
    "SOC_ADMIN": ["SOC_ADMIN", "Admin"],
    "Admin": ["SOC_ADMIN", "Admin"],
    "SOC_ANALYST": ["SOC_ADMIN", "Admin", "SOC_ANALYST", "Analyst"],
    "Analyst": ["SOC_ADMIN", "Admin", "SOC_ANALYST", "Analyst"],
    "INCIDENT_RESPONDER": ["SOC_ADMIN", "Admin", "SOC_ANALYST", "Analyst", "INCIDENT_RESPONDER", "Responder", "Tier1", "Tier2"],
    "Responder": ["SOC_ADMIN", "Admin", "SOC_ANALYST", "Analyst", "INCIDENT_RESPONDER", "Responder", "Tier1", "Tier2"],
    "SECURITY_VIEWER": ["SOC_ADMIN", "Admin", "SOC_ANALYST", "Analyst", "INCIDENT_RESPONDER", "Responder", "SECURITY_VIEWER", "Auditor", "Viewer"],
    "Auditor": ["SOC_ADMIN", "Admin", "SOC_ANALYST", "Analyst", "INCIDENT_RESPONDER", "Responder", "SECURITY_VIEWER", "Auditor", "Viewer"],
    "Viewer": ["SOC_ADMIN", "Admin", "SOC_ANALYST", "Analyst", "INCIDENT_RESPONDER", "Responder", "SECURITY_VIEWER", "Auditor", "Viewer"]
}

def require_roles(allowed_roles: List[str]) -> Callable:
    """
    FastAPI dependency factory enforcing server-side Role-Based Access Control (RBAC).
    Supports canonical SOC roles (SOC_ADMIN, SOC_ANALYST, INCIDENT_RESPONDER, SECURITY_VIEWER)
    and legacy role strings (Admin, Analyst, Auditor, Viewer).
    """
    from app.api.v1.endpoints.auth import get_current_user

    def rbac_dependency(current_user: User = Depends(get_current_user)) -> User:
        expanded_allowed = set()
        for role in allowed_roles:
            expanded_allowed.add(role)
            for key, equivalents in ROLE_MAP.items():
                if role in equivalents:
                    expanded_allowed.update(equivalents)

        user_role = current_user.role or "Analyst"
        if user_role not in expanded_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden. Required role in {allowed_roles}, but user has role '{current_user.role}'."
            )
        return current_user
    return rbac_dependency
