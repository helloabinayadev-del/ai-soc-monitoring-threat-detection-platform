from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
from datetime import datetime, timezone
from app.core.database import Base

class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("log_events.id"), nullable=True, index=True)
    model_version = Column(String, nullable=False, default="IsolationForest-v1.2")
    anomaly_score = Column(Float, nullable=False, default=0.0)
    prediction = Column(String, nullable=False, default="NORMAL") # NORMAL, ANOMALOUS
    threshold = Column(Float, nullable=False, default=65.0)
    contributing_features = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
