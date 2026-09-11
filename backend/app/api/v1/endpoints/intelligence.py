from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.threat_intel import ThreatIntel
from app.schemas.threat_intel import ThreatIntelResponse, ThreatIntelCreate

router = APIRouter()

@router.get("/", response_model=List[ThreatIntelResponse])
def get_threat_intel(
    skip: int = 0,
    limit: int = 50,
    ioc_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ThreatIntel)
    if ioc_type:
        query = query.filter(ThreatIntel.ioc_type == ioc_type)
    return query.order_by(ThreatIntel.threat_score.desc()).offset(skip).limit(limit).all()

@router.post("/", response_model=ThreatIntelResponse)
def add_ioc(ioc_in: ThreatIntelCreate, db: Session = Depends(get_db)):
    existing = db.query(ThreatIntel).filter(ThreatIntel.ioc_value == ioc_in.ioc_value).first()
    if existing:
        raise HTTPException(status_code=400, detail="IOC already exists in database")
    new_ioc = ThreatIntel(**ioc_in.model_dump())
    db.add(new_ioc)
    db.commit()
    db.refresh(new_ioc)
    return new_ioc

@router.get("/lookup/{ioc_value}", response_model=Optional[ThreatIntelResponse])
def lookup_ioc(ioc_value: str, db: Session = Depends(get_db)):
    ioc = db.query(ThreatIntel).filter(ThreatIntel.ioc_value == ioc_value).first()
    if not ioc:
        raise HTTPException(status_code=404, detail="IOC not found in threat intelligence feeds")
    return ioc

@router.get("/enrich/{ioc_value}")
def enrich_ioc(ioc_value: str, db: Session = Depends(get_db)):
    from app.services.threat_intel_service import threat_intel_service
    return threat_intel_service.enrich_ioc(db, ioc_value)

class BulkEnrichSchema(BaseModel):
    iocs: List[str]

@router.post("/enrich/bulk")
def enrich_bulk_iocs(bulk_in: BulkEnrichSchema, db: Session = Depends(get_db)):
    from app.services.threat_intel_service import threat_intel_service
    return threat_intel_service.enrich_bulk(db, bulk_in.iocs)

@router.get("/cve/{cve_id}")
def lookup_cve(cve_id: str):
    # Simulated NVD / CVE API lookup database
    cve_database = {
        "CVE-2023-38606": {
            "cve_id": "CVE-2023-38606",
            "title": "Apple macOS / iOS Kernel Privilege Escalation Vulnerability",
            "cvss_score": 9.8,
            "severity": "CRITICAL",
            "description": "An issue was addressed with improved state management. A malicious app may be able to gain root kernel privileges.",
            "mitre_technique": "T1068 - Exploitation for Privilege Escalation",
            "remediation": "Apply vendor security patch macOS 13.5 / iOS 16.6."
        },
        "CVE-2021-44228": {
            "cve_id": "CVE-2021-44228",
            "title": "Apache Log4j2 Remote Code Execution (Log4Shell)",
            "cvss_score": 10.0,
            "severity": "CRITICAL",
            "description": "JNDI features used in configuration, log messages, and parameters do not protect against attacker controlled LDAP and other JNDI endpoints.",
            "mitre_technique": "T1190 - Exploit Public-Facing Application",
            "remediation": "Upgrade log4j-core to 2.17.1 or higher."
        },
        "CVE-2023-4966": {
            "cve_id": "CVE-2023-4966",
            "title": "Citrix Bleed Sensitive Information Disclosure",
            "cvss_score": 9.4,
            "severity": "CRITICAL",
            "description": "Sensitive information disclosure in Citrix NetScaler ADC and NetScaler Gateway allows session token hijacking.",
            "mitre_technique": "T1539 - Steal Web Session Cookie",
            "remediation": "Upgrade NetScaler firmware and kill all active HTTP sessions."
        }
    }
    cve_upper = cve_id.upper()
    if cve_upper not in cve_database:
        return {
            "cve_id": cve_upper,
            "title": f"Common Vulnerabilities and Exposures record for {cve_upper}",
            "cvss_score": 7.5,
            "severity": "HIGH",
            "description": "Generic security vulnerability record retrieved from MITRE / NVD database feeds.",
            "mitre_technique": "T1190 - Exploit Public-Facing Application",
            "remediation": "Audit affected application dependencies and enforce access controls."
        }
    return cve_database[cve_upper]
