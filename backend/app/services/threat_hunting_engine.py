from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
import re

from app.models.log import LogEvent

class ThreatHuntingEngine:
    def __init__(self):
        self.saved_hunts: List[Dict[str, Any]] = [
            {
                "id": "HUNT-001",
                "name": "Failed Authentication Spikes",
                "description": "Hunts for suspicious failed logon events across all domain controllers.",
                "query": {"event_type": "Authentication", "severity": "HIGH", "search": "failed login"},
                "author": "analyst",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "HUNT-002",
                "name": "Outbound Malicious C2 Egress",
                "description": "Hunts for outbound connections established to external subnets on non-standard ports.",
                "query": {"event_type": "NetworkConnection", "search": "c2 server"},
                "author": "analyst",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]

    def execute_safe_hunt(
        self,
        db: Session,
        source_ip: Optional[str] = None,
        destination_ip: Optional[str] = None,
        user_name: Optional[str] = None,
        hostname: Optional[str] = None,
        severity: Optional[str] = None,
        event_type: Optional[str] = None,
        search: Optional[str] = None,
        time_range_hours: int = 24,
        skip: int = 0,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Executes a safe, read-only telemetry search without executing raw SQL string concatenation.
        """
        # Validate & sanitize inputs
        if search:
            # Prohibit raw SQL manipulation keywords
            forbidden = ["drop ", "delete ", "update ", "insert ", "alter ", "truncate ", ";--", "union select"]
            if any(f_word in search.lower() for f_word in forbidden):
                raise ValueError("Potentially malicious SQL keyword detected in hunting query.")

        query = db.query(LogEvent)

        # Time range filter
        if time_range_hours > 0:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=time_range_hours)
            query = query.filter(LogEvent.timestamp >= cutoff)

        if source_ip:
            query = query.filter(LogEvent.source_ip == source_ip.strip())
        if destination_ip:
            query = query.filter(LogEvent.destination_ip == destination_ip.strip())
        if user_name:
            query = query.filter(LogEvent.user_name == user_name.strip())
        if hostname:
            query = query.filter(LogEvent.hostname == hostname.strip())
        if severity and severity != "ALL":
            query = query.filter(LogEvent.severity == severity.upper())
        if event_type and event_type != "ALL":
            query = query.filter(LogEvent.event_type == event_type)

        if search:
            s_term = f"%{search.strip()}%"
            query = query.filter(
                (LogEvent.raw_message.ilike(s_term)) |
                (LogEvent.source_ip.ilike(s_term)) |
                (LogEvent.destination_ip.ilike(s_term)) |
                (LogEvent.user_name.ilike(s_term)) |
                (LogEvent.hostname.ilike(s_term))
            )

        total_matches = query.count()
        results = query.order_by(LogEvent.timestamp.desc()).offset(skip).limit(limit).all()

        return {
            "query_parameters": {
                "source_ip": source_ip,
                "destination_ip": destination_ip,
                "user_name": user_name,
                "hostname": hostname,
                "severity": severity,
                "event_type": event_type,
                "search": search,
                "time_range_hours": time_range_hours
            },
            "total_matches": total_matches,
            "returned_count": len(results),
            "skip": skip,
            "limit": limit,
            "events": [
                {
                    "id": l.id,
                    "timestamp": l.timestamp.isoformat() if l.timestamp else None,
                    "log_source": l.log_source,
                    "event_type": l.event_type,
                    "source_ip": l.source_ip,
                    "destination_ip": l.destination_ip,
                    "user_name": l.user_name,
                    "hostname": l.hostname,
                    "action": l.action,
                    "severity": l.severity,
                    "is_anomaly": l.is_anomaly,
                    "anomaly_score": l.anomaly_score,
                    "raw_message": l.raw_message,
                    "correlation_id": l.correlation_id
                }
                for l in results
            ]
        }

    def ai_natural_language_hunt(self, nl_query: str) -> Dict[str, Any]:
        """
        Translates natural language hunting requests into structured safe query parameters.
        """
        query_lower = nl_query.lower()
        params = {
            "search": "",
            "event_type": None,
            "severity": None,
            "time_range_hours": 24
        }

        if "failed" in query_lower or "login" in query_lower or "auth" in query_lower:
            params["event_type"] = "Authentication"
            params["search"] = "failed login"
            params["severity"] = "HIGH"
        elif "privilege" in query_lower or "sudo" in query_lower or "root" in query_lower:
            params["event_type"] = "PrivilegeEscalation"
            params["search"] = "sudo"
            params["severity"] = "CRITICAL"
        elif "c2" in query_lower or "beacon" in query_lower or "outbound" in query_lower:
            params["event_type"] = "NetworkConnection"
            params["search"] = "c2 server"
            params["severity"] = "HIGH"
        elif "sqli" in query_lower or "sql" in query_lower or "injection" in query_lower:
            params["event_type"] = "Authentication"
            params["search"] = "sqli"
            params["severity"] = "CRITICAL"
        else:
            params["search"] = nl_query.strip()

        return {
            "natural_language_query": nl_query,
            "generated_safe_parameters": params,
            "explanation": f"AI translated natural language prompt into safe ORM filters: event_type={params['event_type']}, search='{params['search']}'."
        }

    def save_hunt(self, name: str, description: str, query: Dict[str, Any], author: str = "analyst") -> Dict[str, Any]:
        hunt_id = f"HUNT-{len(self.saved_hunts) + 1:03d}"
        hunt_record = {
            "id": hunt_id,
            "name": name,
            "description": description,
            "query": query,
            "author": author,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        self.saved_hunts.append(hunt_record)
        return hunt_record

threat_hunting_engine = ThreatHuntingEngine()
