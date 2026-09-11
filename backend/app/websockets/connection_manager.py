from typing import List, Dict, Any, Optional
from fastapi import WebSocket
from datetime import datetime, timezone
import json
import uuid

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    def sanitize_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Strip sensitive credentials/secrets from broadcast payloads."""
        sanitized = {}
        for key, val in data.items():
            if any(secret_kw in key.lower() for secret_kw in ["password", "token", "secret", "hash"]):
                continue
            if isinstance(val, dict):
                sanitized[key] = self.sanitize_payload(val)
            else:
                sanitized[key] = val
        return sanitized

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a standardized real-time event envelope to all connected SOC clients."""
        disconnected = []
        now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Standard Event Envelope
        event_envelope = {
            "event_type": message.get("type", message.get("event_type", "NEW_SECURITY_EVENT")),
            "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
            "timestamp": now_iso,
            "payload": self.sanitize_payload(message.get("payload", message.get("log", message.get("alert", message))))
        }

        payload_json = json.dumps(event_envelope)

        for connection in self.active_connections:
            try:
                await connection.send_text(payload_json)
            except Exception:
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)

ws_manager = ConnectionManager()
