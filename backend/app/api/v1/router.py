from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, logs, alerts, incidents, intelligence, copilot, 
    analytics, health, audit, correlations, evaluation, feedback, ml, rules, playbooks, mitre, organization
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["System Health Diagnostics"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & RBAC"])
api_router.include_router(logs.router, prefix="/logs", tags=["Log Ingestion & Normalization"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["SIEM Security Alerts"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incident Response Management"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["Threat Intelligence Feeds"])
api_router.include_router(copilot.router, prefix="/copilot", tags=["AI Security Copilot"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["SOC Metrics & Analytics"])
api_router.include_router(audit.router, prefix="/audit", tags=["Security Audit Trail"])
api_router.include_router(correlations.router, prefix="/correlations", tags=["Event Correlation Engine"])
api_router.include_router(evaluation.router, prefix="/evaluation", tags=["Quantitative Model & SOC Evaluation"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Analyst Feedback Tuning"])
api_router.include_router(ml.router, prefix="/ml", tags=["ML Model Management & Status"])
api_router.include_router(rules.router, prefix="/rules", tags=["Detection Engineering & Rule Management"])
api_router.include_router(playbooks.router, prefix="/playbooks", tags=["SOAR Response Playbooks & Automation Engine"])
api_router.include_router(mitre.router, prefix="/mitre", tags=["MITRE ATT&CK Mapping & Attack Chain Analysis"])
api_router.include_router(organization.router, prefix="/organizations", tags=["Multi-Tenant Organization Management"])

