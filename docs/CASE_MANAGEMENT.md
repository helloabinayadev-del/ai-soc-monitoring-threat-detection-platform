# Advanced SOC Case Management & Forensics Specification

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Case Lifecycle, Evidence Cryptographic Integrity, Chain of Custody, & Reporting  

---

## 1. Case Investigation & Evidence Pipeline Flow

```
[ SIEM Security Alert ]
           ↓
[ Create Incident Case Ticket (INC-XXXXXX) ]
           ↓
[ Attach Raw Log Telemetry & Evidence (POST /api/v1/incidents/{id}/evidence) ]
           ↓
[ Calculate Cryptographic SHA-256 Hash (Evidence Integrity Verification) ]
           ↓
[ Record Chain-of-Custody Audit Entry (audit_logs Table) ]
           ↓
[ AI Copilot Case Summary & ATT&CK Mapping ]
           ↓
[ Analyst Finding Decision (CONFIRMED / FALSE_POSITIVE / INCONCLUSIVE) ]
           ↓
[ Generate Forensic Case Investigation Report (SHA-256 Report Hash) ]
```

---

## 2. Evidence Integrity & Chain of Custody

- **SHA-256 Cryptographic Hash**: Every raw evidence attachment calculates a 256-bit SHA-256 hash (`sha256_hash`) over raw text content.
- **Audit Logging**: Every evidence attachment and status change writes an auditable record to `audit_logs` containing `user`, `timestamp`, `action`, `resource_id`, and `hash`.
- **Report Integrity**: Generating a case report calculates a report-level SHA-256 checksum over the entire JSON report payload.
- **Content Grounding**: Reports explicitly label sections to distinguish human `ANALYST FINDINGS` from `AI-GENERATED CONTENT`.
