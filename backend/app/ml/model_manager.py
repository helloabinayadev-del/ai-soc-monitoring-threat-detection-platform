import os
import joblib
from typing import Dict, Any, Optional
from app.ml.anomaly_detector import ml_anomaly_detector, IsolationForestAnomalyDetector, MODEL_VERSION

class ModelManager:
    """
    Manages ML model lifecycle, serialization, dynamic threshold adjustment, and status reports.
    """
    def __init__(self, model_dir: str = "app/ml/saved_models"):
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        self.active_model = ml_anomaly_detector

    def get_model_status(self) -> Dict[str, Any]:
        return {
            "model_name": "IsolationForest",
            "model_version": self.active_model.model_version,
            "is_fitted": self.active_model.is_fitted,
            "threshold": self.active_model.threshold,
            "contamination": self.active_model.contamination,
            "n_estimators": self.active_model.model.n_estimators,
            "features_count": len(self.active_model.baseline_mean) if self.active_model.is_fitted else 0
        }

    def update_threshold(self, new_threshold: float) -> float:
        clamped = max(10.0, min(95.0, new_threshold))
        self.active_model.threshold = clamped
        return clamped

model_manager = ModelManager()
