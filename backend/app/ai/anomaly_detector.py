import numpy as np
from typing import Dict, Any, Tuple, List, Optional
from app.ml.anomaly_detector import ml_anomaly_detector, IsolationForestAnomalyDetector

class LogAnomalyDetector:
    """
    Adapter wrapper around IsolationForestAnomalyDetector in app.ml for backward compatibility.
    """
    def __init__(self):
        self.engine = ml_anomaly_detector

    @property
    def is_fitted(self) -> bool:
        return self.engine.is_fitted

    def extract_features(self, log_dict: Dict[str, Any]) -> np.ndarray:
        from app.ml.feature_engineering import feature_extractor
        return feature_extractor.extract_features(log_dict)

    def predict(self, log_dict: Dict[str, Any], history: Optional[List[Dict[str, Any]]] = None) -> Tuple[str, float]:
        """
        Returns (is_anomaly, anomaly_score)
        anomaly_score ranges from 0.0 (perfectly normal) to 100.0 (highly anomalous)
        """
        res = self.engine.predict(log_dict, history=history)
        return res["prediction"], res["anomaly_score"]

    def predict_detailed(self, log_dict: Dict[str, Any], history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        return self.engine.predict(log_dict, history=history)

# Singleton instance
anomaly_detector = LogAnomalyDetector()
