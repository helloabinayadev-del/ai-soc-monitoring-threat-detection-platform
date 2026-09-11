import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class SecurityFeatureExtractor:
    """
    Extracts numerical security features from raw/parsed log events.
    Features:
    0: event_frequency (count of recent events from same source IP)
    1: failed_login_count (count of authentication failures from source IP)
    2: successful_login_count (count of successful authentications)
    3: source_port_norm (normalized source port)
    4: destination_port_norm (normalized destination port)
    5: event_type_code (numerical encoding for event type)
    6: severity_numeric (numerical mapping for severity)
    7: is_failed_auth (binary flag for failed auth / deny action)
    8: time_hour_norm (hour of day normalized 0.0 - 1.0)
    9: payload_length_norm (message length normalized 0.0 - 1.0)
    """

    FEATURE_NAMES = [
        "event_frequency",
        "failed_login_count",
        "successful_login_count",
        "source_port_norm",
        "destination_port_norm",
        "event_type_code",
        "severity_numeric",
        "is_failed_auth",
        "time_hour_norm",
        "payload_length_norm"
    ]

    EVENT_TYPE_MAP = {
        "AUTHENTICATION": 1.0,
        "NETWORKCONNECTION": 2.0,
        "PROCESSCREATION": 3.0,
        "PRIVILEGEESCALATION": 4.0,
        "SYSTEM": 5.0
    }

    SEVERITY_MAP = {
        "INFORMATIONAL": 1.0,
        "LOW": 2.0,
        "MEDIUM": 3.0,
        "HIGH": 4.0,
        "CRITICAL": 5.0
    }

    def extract_features(self, log_dict: Dict[str, Any], history: Optional[List[Dict[str, Any]]] = None) -> np.ndarray:
        src_ip = log_dict.get("source_ip") or "0.0.0.0"
        msg = str(log_dict.get("raw_message") or "")
        msg_lower = msg.lower()
        action = str(log_dict.get("action") or "").upper()
        event_type = str(log_dict.get("event_type") or "").upper()
        severity = str(log_dict.get("severity") or "INFORMATIONAL").upper()

        # Historical context calculation
        event_freq = 1.0
        failed_count = 0.0
        success_count = 0.0

        if history:
            for item in history:
                if item.get("source_ip") == src_ip:
                    event_freq += 1.0
                    item_action = str(item.get("action") or "").upper()
                    item_msg = str(item.get("raw_message") or "").lower()
                    if item_action == "FAIL" or "failed" in item_msg:
                        failed_count += 1.0
                    elif item_action == "ALLOW" or item_action == "SUCCESS":
                        success_count += 1.0

        # Current log action check
        is_failed = 1.0 if (action in ["FAIL", "DENY"] or "failed" in msg_lower or "failure" in msg_lower) else 0.0
        if is_failed:
            failed_count += 1.0

        # Ports
        src_port = float(log_dict.get("source_port") or 80) / 65535.0
        dst_port = float(log_dict.get("destination_port") or 443) / 65535.0

        # Event type & severity codes
        evt_code = self.EVENT_TYPE_MAP.get(event_type, 0.0)
        sev_code = self.SEVERITY_MAP.get(severity, 1.0)

        # Time of day
        ts = log_dict.get("timestamp")
        if isinstance(ts, datetime):
            hour = ts.hour
        else:
            hour = datetime.now(timezone.utc).hour
        time_hour = hour / 24.0

        # Payload length
        payload_len = min(1.0, len(msg) / 1000.0)

        features = [
            event_freq,
            failed_count,
            success_count,
            src_port,
            dst_port,
            evt_code,
            sev_code,
            is_failed,
            time_hour,
            payload_len
        ]

        return np.array([features], dtype=np.float64)

feature_extractor = SecurityFeatureExtractor()
