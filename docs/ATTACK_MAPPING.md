# MITRE ATT&CK Technique Mapping & Attack Chain Analysis Specification

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Framework Taxonomy, Evidence-Based Mapping, Attack Progression, & Coverage Matrix  

---

## 1. Evidence-Based ATT&CK Mapping Pipeline Flow

```
[ Correlated Security Alerts ]
              ↓
[ MITRE ATT&CK Tag Extraction (Tactic, Technique ID) ]
              ↓
[ Evidence Grounding & Confidence Evaluation ]
       ├── Grounded Log Evidence ──→ Assign HIGH_CONFIDENCE / CONFIRMED
       └── Uncertain Inference   ──→ Assign POSSIBLE / AI RECOMMENDED
              ↓
[ Multi-Stage Attack Chain Progression Engine ]
              ↓
[ Detection Coverage Matrix & Gap Analysis View ]
```

---

## 2. Confidence States & Progression Statuses

### Mapping Confidence Levels:
- **`CONFIRMED`**: Analyst-validated technique match backed by empirical evidence.
- **`HIGH_CONFIDENCE`**: Signature rule + ML anomaly match (`HYBRID` detection source).
- **`POSSIBLE`**: Single log keyword or unverified heuristic match.
- **`UNSUPPORTED`**: Insufficient evidence to justify ATT&CK technique mapping.
- **`NOT_MAPPED`**: General operational log with no security threat mapping.

### Attack Chain Stage Statuses:
- **`OBSERVED`**: Explicit correlated alert present in telemetry for this tactical stage.
- **`SUPPORTED`**: Threat intelligence or process lineage indicates probable stage execution.
- **`POSSIBLE`**: Logical precursor to a later observed stage.
- **`MISSING_EVIDENCE`**: No log telemetry observed for this tactical stage.
- **`NOT_ESTABLISHED`**: Unsubstantiated progression step.
