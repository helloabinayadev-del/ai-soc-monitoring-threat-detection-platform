# Threat Intelligence & IOC Enrichment Engine Specification

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Provider Abstraction, IOC Normalization, Result States, & Risk Integration  

---

## 1. IOC Enrichment Pipeline Flow

```
[ Security Event Telemetry ]
            ↓
[ IOC Extraction (Source IP, Destination IP, Domain, Hash) ]
            ↓
[ IOC Validation & Normalization (Trim, Lowercase, Regex Check) ]
            ↓
[ Local DB Cache Lookup (threat_intel Table) ]
       ├── Match Found ──→ Return Cached Reputation Record
       └── Cache Miss  ──→ Check External Provider API (AbuseIPDB / AlienVault)
            ↓
[ Standardized Result Record (MALICIOUS / SUSPICIOUS / BENIGN / NOT_CONFIGURED) ]
            ↓
[ Alert Risk Score Enrichment (+20 pts Risk Boost for Malicious IOCs) ]
            ↓
[ Grounded AI Copilot Threat Analysis ]
```

---

## 2. Result States & Grounded AI Intelligence

To prevent hallucinated reputation or ungrounded classifications:
- **`MALICIOUS`**: Confirmed malicious indicator (Score $\ge 75/100$).
- **`SUSPICIOUS`**: Moderately suspicious indicator ($25 \le \text{Score} < 75$).
- **`BENIGN`**: Clean background indicator ($\text{Score} < 25$).
- **`UNKNOWN`**: Indicator evaluated but reputation unlisted.
- **`NO_DATA`**: Invalid or unparseable IOC format.
- **`UNAVAILABLE`**: External threat feed API rate limited (429), timed out, or connection failed.
- **`NOT_CONFIGURED`**: `THREAT_INTEL_API_KEY` environment variable is not configured.

---

## 3. Secret Management & Security

- **Environment Key**: External API keys are read strictly from `os.getenv("THREAT_INTEL_API_KEY")`.
- **Frontend Safety**: API keys are never passed to or exposed in frontend JavaScript bundles. All lookups execute server-side.
