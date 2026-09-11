from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from datetime import datetime
from app.core.database import Base

class ThreatIntel(Base):
    __tablename__ = "threat_intel"

    id = Column(Integer, primary_key=True, index=True)
    ioc_value = Column(String, unique=True, index=True, nullable=False) # IP, Hash, Domain, URL
    ioc_type = Column(String, index=True, nullable=False) # IP, MD5, SHA256, DOMAIN, URL
    threat_type = Column(String, nullable=True) # Botnet, Ransomware, C2, Phishing, Malware
    threat_score = Column(Float, default=75.0) # 0 to 100
    source_feed = Column(String, default="AlienVault OTX / AbuseIPDB / Custom")
    description = Column(Text, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
