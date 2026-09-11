from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.core.database import get_db
from app.ml.model_manager import model_manager
from app.ml.anomaly_detector import ml_anomaly_detector
from app.models.ml_prediction import MLPrediction

router = APIRouter()

class ThresholdUpdate(BaseModel):
    threshold: float

class LogAnalyzeRequest(BaseModel):
    log_source: Optional[str] = "WindowsEvent"
    event_type: Optional[str] = "Authentication"
    source_ip: Optional[str] = "192.168.1.1"
    destination_ip: Optional[str] = "10.0.0.5"
    source_port: Optional[int] = 49152
    destination_port: Optional[int] = 445
    action: Optional[str] = "FAIL"
    severity: Optional[str] = "HIGH"
    raw_message: str

@router.get("/status")
def get_ml_status():
    return model_manager.get_model_status()

@router.post("/threshold")
def update_threshold(payload: ThresholdUpdate):
    updated = model_manager.update_threshold(payload.threshold)
    return {
        "status": "success",
        "threshold": updated,
        "message": f"Anomaly detection threshold updated to {updated}"
    }

@router.post("/analyze")
def analyze_log_payload(payload: LogAnalyzeRequest):
    """
    On-demand real-time ML anomaly detection analysis for raw security log payloads.
    Returns anomaly score, prediction, model version, timestamp, and transparent feature explanations.
    """
    log_dict = payload.model_dump()
    ml_res = ml_anomaly_detector.predict(log_dict)
    return ml_res

@router.get("/results")
def get_ml_results(
    skip: int = 0,
    limit: int = 50,
    prediction: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Returns persisted ML prediction history from the database.
    """
    query = db.query(MLPrediction)
    if prediction and prediction != "ALL":
        query = query.filter(MLPrediction.prediction == prediction)
    records = query.order_by(MLPrediction.created_at.desc()).offset(skip).limit(limit).all()
    return records
