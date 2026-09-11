from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
from datetime import datetime, timezone
from app.core.database import Base

class ModelEvaluationRecord(Base):
    __tablename__ = "model_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    dataset_name = Column(String, nullable=False, default="UNSW-NB15 Benchmark Subset")
    model_name = Column(String, nullable=False, default="IsolationForest-v1")
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    false_positive_rate = Column(Float, nullable=False)
    false_negative_rate = Column(Float, nullable=False)
    mttd_seconds = Column(Float, nullable=False)
    mttr_seconds = Column(Float, nullable=False)
    alert_reduction_percent = Column(Float, nullable=False)
    metrics_json = Column(JSON, nullable=True)

class AnalystFeedback(Base):
    __tablename__ = "analyst_feedback"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("security_alerts.id"), nullable=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True, index=True)
    analyst_username = Column(String, nullable=False, default="analyst")
    feedback_type = Column(String, nullable=False) # TRUE_POSITIVE, FALSE_POSITIVE, RISK_TOO_HIGH, RISK_TOO_LOW
    comments = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
