from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class CopilotQuery(BaseModel):
    query: str
    context_alert_id: Optional[int] = None
    context_incident_id: Optional[int] = None

class CopilotResponse(BaseModel):
    answer: str
    action_items: List[str]
    mitre_references: List[str]
    confidence_score: float
    analysis_details: Dict[str, Any]
    # Enhanced 10-Point Evidence-Driven Fields
    what_happened: Optional[str] = None
    why_generated: Optional[str] = None
    evidence_items: Optional[List[str]] = None
    risk_explanation: Optional[str] = None
    correlated_events_summary: Optional[str] = None
    threat_intel_context: Optional[str] = None
    investigation_steps: Optional[List[str]] = None
    recommended_remediation: Optional[List[str]] = None
    uncertainty_statement: Optional[str] = None
