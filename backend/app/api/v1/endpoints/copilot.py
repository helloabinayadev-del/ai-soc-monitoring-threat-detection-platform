from fastapi import APIRouter, Depends
from app.schemas.copilot import CopilotQuery, CopilotResponse
from app.services.copilot_service import copilot_service

router = APIRouter()

@router.post("/query", response_model=CopilotResponse)
def query_copilot(query_in: CopilotQuery):
    response = copilot_service.analyze_query(
        query=query_in.query,
        alert_data=query_in.context_alert_id,
        incident_data=query_in.context_incident_id
    )
    return response
