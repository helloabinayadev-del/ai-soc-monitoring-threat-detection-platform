# Detection Engineering & Rule Management Specification

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Signature Rule Engine, Safe Condition Evaluation, & Rule Lifecycle  

---

## 1. Detection Rule Architecture & Lifecycle

Detection rules are executed in `app/ai/threat_classifier.py` during raw log ingestion.

```
[ Raw Security Log Payload ]
             ↓
[ Rule Lifecycle Filter: Status == "ACTIVE" ]
             ↓
[ Safe Condition Evaluator (equals, contains, starts_with, ends_with) ]
             ↓
[ Match Result Generated (Rule ID, Version, Explanation) ]
             ↓
[ Risk Engine Enrichment & ML Anomaly Combination (HYBRID Source Tag) ]
```

### Lifecycle States:
- **`DRAFT`**: Rule is defined but excluded from live detection.
- **`ACTIVE`**: Rule actively evaluates incoming log events.
- **`DISABLED`**: Rule evaluation is paused by SOC administrator.
- **`DEPRECATED`**: Rule is archived for historical traceability.

---

## 2. Safe Condition Evaluation (No `eval()`)

To prevent arbitrary code execution vulnerabilities, rule conditions use safe deterministic comparisons rather than Python `eval()` or shell execution:
- **`equals`**: Exact string match (`raw_message == "failed login"`).
- **`contains`**: Substring search (`"sudo" in raw_message`).
- **`starts_with`**: Substring prefix check.
- **`ends_with`**: Substring suffix check.

---

## 3. Rule Testing & Versioning

- **Rule Testing API (`POST /api/v1/rules/test`)**: Tests a candidate rule against arbitrary test log payloads without creating live alerts, returning `MATCH` or `NO_MATCH` with an explanation.
- **Version Tracking**: Modifying an active rule increments its `version` counter (e.g. `v1` $\rightarrow$ `v2`), allowing analysts to trace historical alerts back to the exact version of the rule that triggered them.
