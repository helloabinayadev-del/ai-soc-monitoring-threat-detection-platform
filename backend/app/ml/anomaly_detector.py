import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime, timezone
import os
import joblib

from app.ml.feature_engineering import feature_extractor, SecurityFeatureExtractor
from app.ml.preprocessing import LogPreprocessor

MODEL_VERSION = "IsolationForest-v1.2"
DEFAULT_THRESHOLD = 65.0 # Configurable anomaly threshold (0 - 100 scale)

class IsolationForestAnomalyDetector:
    """
    Scikit-Learn IsolationForest Anomaly Detector for tabular log metrics.
    Produces:
    - anomaly_score (0.0 to 100.0)
    - prediction ("ANOMALOUS" or "NORMAL")
    - model_version
    - transparent feature attribution breakdown
    """

    def __init__(self, threshold: float = DEFAULT_THRESHOLD, contamination: float = 0.05):
        self.model_version = MODEL_VERSION
        self.threshold = threshold
        self.contamination = contamination
        self.model = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=42,
            n_jobs=-1
        )
        self.preprocessor = LogPreprocessor()
        self.is_fitted = False
        self._bootstrap_normal_baseline()

    def _bootstrap_normal_baseline(self):
        """
        Bootstrap model using realistic baseline normal security telemetry.
        """
        np.random.seed(42)
        n_samples = 300
        
        # Synthetic baseline normal metrics:
        # event_freq ~ 1-3, failed_count ~ 0, success_count ~ 1-5,
        # ports ~ 80/443, evt_code ~ 1-3, sev ~ 1-2, is_failed ~ 0, hour ~ normal, payload ~ 0.1
        freq = np.random.uniform(1.0, 3.0, (n_samples, 1))
        failed = np.zeros((n_samples, 1))
        success = np.random.uniform(1.0, 5.0, (n_samples, 1))
        src_p = np.random.uniform(40000, 65000, (n_samples, 1)) / 65535.0
        dst_p = np.random.choice([80/65535.0, 443/65535.0, 53/65535.0], size=(n_samples, 1))
        evt_type = np.random.choice([1.0, 2.0, 3.0], size=(n_samples, 1))
        sev = np.random.choice([1.0, 2.0], size=(n_samples, 1))
        is_fail = np.zeros((n_samples, 1))
        time_h = np.random.uniform(0.3, 0.8, (n_samples, 1))
        payload = np.random.uniform(0.05, 0.2, (n_samples, 1))

        baseline_X = np.hstack([freq, failed, success, src_p, dst_p, evt_type, sev, is_fail, time_h, payload])
        scaled_X = self.preprocessor.fit_transform(baseline_X)
        self.model.fit(scaled_X)
        self.is_fitted = True
        self.baseline_mean = np.mean(baseline_X, axis=0)
        self.baseline_std = np.std(baseline_X, axis=0) + 1e-5

    def predict(self, log_dict: Dict[str, Any], history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Runs ML Anomaly Detection on a log event.
        Returns detailed dictionary:
        {
          "anomaly_score": float (0-100),
          "prediction": "ANOMALOUS" | "NORMAL",
          "model_version": str,
          "prediction_timestamp": str,
          "threshold": float,
          "contributing_features": List[Dict]
        }
        """
        raw_features = feature_extractor.extract_features(log_dict, history=history)
        scaled_features = self.preprocessor.transform(raw_features)

        # Isolation Forest decision_function (higher score = more normal, negative = anomaly)
        raw_decision = float(self.model.decision_function(scaled_features)[0])

        # Calibrate raw_decision (-0.35 to 0.35) into 0-100 anomaly score scale
        # decision score near -0.2+ maps to 90+, decision score +0.2 maps to <20
        anomaly_score = max(0.0, min(100.0, round((0.35 - raw_decision) * 142.8, 2)))

        is_anomalous = anomaly_score >= self.threshold or self.model.predict(scaled_features)[0] == -1
        prediction = "ANOMALOUS" if is_anomalous else "NORMAL"

        # Transparent Feature Attribution
        feature_attribution = self.explain_features(raw_features[0])

        return {
            "anomaly_score": anomaly_score,
            "prediction": prediction,
            "model_version": self.model_version,
            "threshold": self.threshold,
            "prediction_timestamp": datetime.now(timezone.utc).isoformat(),
            "contributing_features": feature_attribution,
            "raw_features": raw_features[0].tolist()
        }

    def explain_features(self, feature_vec: np.ndarray) -> List[Dict[str, Any]]:
        """
        Transparent feature-attribution explanation comparing current feature values to baseline distributions.
        """
        attributions = []
        z_scores = np.abs((feature_vec - self.baseline_mean) / self.baseline_std)

        # Map top deviations
        for idx, (val, z, name) in enumerate(zip(feature_vec, z_scores, SecurityFeatureExtractor.FEATURE_NAMES)):
            if z > 1.2:
                description = self._get_feature_description(name, val)
                attributions.append({
                    "feature": name,
                    "value": round(float(val), 4),
                    "z_score": round(float(z), 2),
                    "contribution_weight": round(min(1.0, float(z) / 5.0), 2),
                    "description": description
                })

        # Sort by z-score descending
        attributions.sort(key=lambda x: x["z_score"], reverse=True)
        return attributions[:5]

    def _get_feature_description(self, name: str, value: float) -> str:
        if name == "failed_login_count" and value > 0:
            return f"Repeated authentication failures observed ({int(value)} failed attempts)"
        elif name == "event_frequency" and value > 2:
            return f"High event frequency burst ({int(value)} events in window)"
        elif name == "is_failed_auth" and value == 1.0:
            return "Event action signifies explicit security deny/failure"
        elif name == "severity_numeric" and value >= 4.0:
            return "Log payload contains HIGH or CRITICAL severity rating"
        elif name == "payload_length_norm" and value > 0.4:
            return "Unusually large payload length detected"
        elif name == "destination_port_norm":
            return f"Unusual target port ratio ({round(value * 65535)})"
        return f"Abnormal metric deviation for {name} ({round(value, 2)})"

ml_anomaly_detector = IsolationForestAnomalyDetector()
