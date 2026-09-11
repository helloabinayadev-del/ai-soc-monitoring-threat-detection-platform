import re
import os
import requests
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.threat_intel import ThreatIntel

class ThreatIntelService:
    def __init__(self):
        self.api_key = os.getenv("THREAT_INTEL_API_KEY", None)

    def validate_and_normalize_ioc(self, raw_ioc: str) -> Tuple[str, str, bool]:
        """
        Validates and normalizes IOC values.
        Returns (normalized_value, ioc_type, is_valid)
        """
        if not raw_ioc:
            return "", "UNKNOWN", False

        ioc = raw_ioc.strip()
        ioc_lower = ioc.lower()

        # 1. IPv4 Regex
        ipv4_pattern = r"^^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        if re.match(ipv4_pattern, ioc):
            return ioc, "IPv4", True

        # 2. IPv6 Regex
        ipv6_pattern = r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"
        if re.match(ipv6_pattern, ioc):
            return ioc_lower, "IPv6", True

        # 3. Hashes (MD5: 32 hex, SHA1: 40 hex, SHA256: 64 hex)
        if re.match(r"^[a-fA-F0-9]{64}$", ioc):
            return ioc_lower, "SHA256", True
        if re.match(r"^[a-fA-F0-9]{40}$", ioc):
            return ioc_lower, "SHA1", True
        if re.match(r"^[a-fA-F0-9]{32}$", ioc):
            return ioc_lower, "MD5", True

        # 4. Domain Regex
        domain_pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
        if re.match(domain_pattern, ioc):
            return ioc_lower, "Domain", True

        # 5. URL
        if ioc_lower.startswith("http://") or ioc_lower.startswith("https://"):
            return ioc_lower, "URL", True

        return ioc_lower, "UNKNOWN", False

    def enrich_ioc(self, db: Session, raw_ioc: str) -> Dict[str, Any]:
        """
        Main IOC enrichment engine combining local cache lookup with external feed integration.
        Returns standardized Threat Intelligence Enrichment Record.
        """
        normalized_val, ioc_type, is_valid = self.validate_and_normalize_ioc(raw_ioc)
        now_iso = datetime.now(timezone.utc).isoformat()

        if not is_valid:
            return {
                "ioc_value": raw_ioc,
                "normalized_value": normalized_val,
                "ioc_type": ioc_type,
                "provider": "Local Validator",
                "result_state": "NO_DATA",
                "threat_score": 0.0,
                "confidence": "LOW",
                "categories": ["Invalid Format"],
                "lookup_timestamp": now_iso
            }

        # 1. Local Database Threat Intelligence Cache Lookup
        cached_ioc = db.query(ThreatIntel).filter(ThreatIntel.ioc_value == normalized_val).first()
        if cached_ioc:
            score = cached_ioc.threat_score or 75.0
            state = "MALICIOUS" if score >= 80.0 else ("SUSPICIOUS" if score >= 50.0 else "BENIGN")
            return {
                "ioc_value": raw_ioc,
                "normalized_value": normalized_val,
                "ioc_type": cached_ioc.ioc_type or ioc_type,
                "provider": cached_ioc.source_feed or "Local Threat Intel Feed",
                "result_state": state,
                "threat_score": score,
                "confidence": "HIGH",
                "categories": [cached_ioc.threat_type or "General Threat"],
                "description": cached_ioc.description,
                "last_updated": cached_ioc.last_updated.isoformat() if cached_ioc.last_updated else now_iso,
                "lookup_timestamp": now_iso
            }

        # 2. External Provider Lookup Integration (if configured)
        if not self.api_key:
            return {
                "ioc_value": raw_ioc,
                "normalized_value": normalized_val,
                "ioc_type": ioc_type,
                "provider": "External Feed",
                "result_state": "NOT_CONFIGURED",
                "threat_score": 0.0,
                "confidence": "NONE",
                "categories": ["API Key Not Set"],
                "lookup_timestamp": now_iso
            }

        # Safe External API call logic (handling timeouts / rate limits)
        try:
            url = f"https://api.abuseipdb.com/api/v2/check?ipAddress={normalized_val}"
            headers = {"Key": self.api_key, "Accept": "application/json"}
            res = requests.get(url, headers=headers, timeout=3.0)

            if res.status_code == 200:
                data = res.json().get("data", {})
                score = float(data.get("abuseConfidenceScore", 0))
                state = "MALICIOUS" if score >= 75.0 else ("SUSPICIOUS" if score >= 25.0 else "BENIGN")
                return {
                    "ioc_value": raw_ioc,
                    "normalized_value": normalized_val,
                    "ioc_type": ioc_type,
                    "provider": "AbuseIPDB External API",
                    "result_state": state,
                    "threat_score": score,
                    "confidence": "HIGH",
                    "categories": data.get("reports", []),
                    "lookup_timestamp": now_iso
                }
            elif res.status_code == 429:
                return {
                    "ioc_value": raw_ioc,
                    "normalized_value": normalized_val,
                    "ioc_type": ioc_type,
                    "provider": "AbuseIPDB External API",
                    "result_state": "UNAVAILABLE",
                    "threat_score": 0.0,
                    "confidence": "NONE",
                    "categories": ["Rate Limit Exceeded (HTTP 429)"],
                    "lookup_timestamp": now_iso
                }
            else:
                return {
                    "ioc_value": raw_ioc,
                    "normalized_value": normalized_val,
                    "ioc_type": ioc_type,
                    "provider": "AbuseIPDB External API",
                    "result_state": "UNAVAILABLE",
                    "threat_score": 0.0,
                    "confidence": "NONE",
                    "categories": [f"API Error HTTP {res.status_code}"],
                    "lookup_timestamp": now_iso
                }
        except Exception as e:
            return {
                "ioc_value": raw_ioc,
                "normalized_value": normalized_val,
                "ioc_type": ioc_type,
                "provider": "External Feed",
                "result_state": "UNAVAILABLE",
                "threat_score": 0.0,
                "confidence": "NONE",
                "categories": [f"Connection Failed: {str(e)}"],
                "lookup_timestamp": now_iso
            }

    def enrich_bulk(self, db: Session, raw_iocs: List[str]) -> List[Dict[str, Any]]:
        """Bulk enrichment supporting max 20 IOCs per batch."""
        capped_iocs = raw_iocs[:20]
        return [self.enrich_ioc(db, ioc) for ioc in capped_iocs]

threat_intel_service = ThreatIntelService()
