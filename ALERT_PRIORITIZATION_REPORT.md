# Upgrade 2 — Intelligent Alert Prioritization & Risk Scoring Report

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Upgrade Focus**: UPGRADE 2 — INTELLIGENT ALERT PRIORITIZATION & RISK SCORING  
**Completion Date**: August 27, 2026  

---

## 1. Existing Alert Architecture (Before Upgrade)
- Originally, SIEM alerts derived static risk scores assigned directly by threat rules or raw anomaly scores.
- There was no multi-factor evidence weighting, no priority classification (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), no detection source classification (`RULE_BASED`, `ML_ANOMALY`, `HYBRID`), and no transparent itemization of contributing factors explaining WHY a specific score was assigned.

---

## 2. Changes Made
- Implemented `IntelligentAlertPrioritizationService` in `backend/app/services/prioritization_service.py` computing transparent 0–100 risk scores based on 7 empirical evidence factors.
- Added priority classification (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) using configurable score cutoffs.
- Added detection source classification (`RULE_BASED`, `ML_ANOMALY`, `HYBRID`).
- Itemized `risk_factors` list explaining the exact points contributed by severity, ML anomaly score, event repetition, asset criticality, threat intelligence matches, and event correlation.
- Updated `SecurityAlert` database model and API schemas (`AlertBase`, `AlertResponse`).
- Updated API endpoints in `backend/app/api/v1/endpoints/alerts.py` supporting priority, detection source, and `min_risk_score` filters.
- Enhanced Frontend `AlertCard.tsx` with an interactive **Transparent Risk Score Breakdown** drawer and priority badges.
- Created dedicated test suite `backend/tests/test_prioritization.py` covering 12 core test scenarios and edge cases.

---

## 3. Risk-Scoring Methodology & Formula

$$ \text{Risk Score} = \min\Big(100.0, \big(\text{Rule/Base Sev Score} \times 0.40 + \text{ML Anomaly Score} \times 0.35 + \text{Burst Points} + \text{TI Points} + \text{Corr Points}\big) \times \text{Asset Multiplier}\Big) $$

---

## 4. Risk Factors & Weights Table

| Factor # | Risk Factor Name | Formula / Points | Max Weight Contribution |
|---|---|---|---|
| 1 | **Base Rule / Event Severity** | `Base Score * 0.40` (INFORMATIONAL=10, LOW=25, MEDIUM=50, HIGH=75, CRITICAL=92) | 36.8 pts |
| 2 | **Isolation Forest ML Anomaly Score** | `Anomaly Score * 0.35` (Score range 0–100) | 35.0 pts |
| 3 | **Repeated Event Frequency Burst** | `min(15.0, (frequency_count - 1) * 3.5)` | 15.0 pts |
| 4 | **Asset Criticality Multiplier** | Multiplier scale (DC=1.3x, Prod Server=1.25x, Workstation=1.0x) | 1.30x Multiplier |
| 5 | **Threat Intelligence Match** | Known Malicious Indicator Match | +20.0 pts |
| 6 | **Event Correlation Strength** | `min(25.0, (correlated_count - 1) * 6.0)` | 25.0 pts |
| 7 | **Analyst Feedback Tuning** | Historical analyst calibration bias | ±15.0 pts |

---

## 5. Priority Classification Thresholds

| Priority Rank | Risk Score Range | Color Badge | Recommended Action |
|---|---|---|---|
| **CRITICAL** | **85.0 – 100.0** | Red (`bg-red-950 text-red-400`) | Immediate automated EDR isolation & SOC Tier 3 escalation |
| **HIGH** | **65.0 – 84.9** | Orange (`bg-orange-950 text-orange-400`) | Active triage required within 15 minutes |
| **MEDIUM** | **40.0 – 64.9** | Yellow (`bg-yellow-950 text-yellow-400`) | Standard analyst queue triage |
| **LOW** | **0.0 – 39.9** | Slate (`bg-slate-800 text-slate-300`) | Informational logging / audit record |

---

## 6. ML Integration & Detection Source Classification
- **Rule Detection Result + ML Anomaly Result** are combined during alert creation.
- **Detection Source Tags**:
  - `RULE_BASED`: Alert triggered solely by security signature rule.
  - `ML_ANOMALY`: Alert triggered solely by Isolation Forest score > 65.0.
  - `HYBRID`: Alert triggered by both rule signature match AND Isolation Forest score > 65.0.

---

## 7. API Changes
- `GET /api/v1/alerts/?priority=CRITICAL`: Filter alerts by priority level.
- `GET /api/v1/alerts/?detection_source=HYBRID`: Filter alerts by detection mechanism.
- `GET /api/v1/alerts/?min_risk_score=75.0`: Filter alerts above risk threshold.
- `GET /api/v1/alerts/{id}`: Returns alert detail containing itemized `risk_factors` array.

---

## 8. Database Schema
Updated `security_alerts` table:
- `risk_score` (Float, default=50.0)
- `priority` (String, default="MEDIUM", indexed)
- `detection_source` (String, default="RULE_BASED", indexed)
- `risk_factors` (JSON, nullable=True)
- `anomaly_score` (Float, default=0.0)
- `correlation_id` (String, indexed)

---

## 9. Frontend Integration
- **Alert Cards**: Render priority badge (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), detection source tag (`Src: RULE_BASED`, `Src: ML_ANOMALY`, `Src: HYBRID`), and correlation ID badge.
- **Transparent Breakdown Drawer**: Interactive Info icon expands the exact contributing factors breakdown list.

---

## 10. Test Results & Edge Cases Verified
All 12 test scenarios in `backend/tests/test_prioritization.py` executed successfully:
1. Low-severity event -> Priority `LOW` (Passed)
2. Medium-severity event -> Priority `MEDIUM` (Passed)
3. High-severity event -> Priority `HIGH` (Passed)
4. Critical event -> Priority `CRITICAL` (Passed)
5. High anomaly score contribution (Passed)
6. Repeated event burst points (Passed)
7. Threat Intelligence match +20 pts (Passed)
8. Correlated event chain points (Passed)
9. Missing optional risk factors fallback (Passed — failsafe operation)
10. Unknown severity handling (Passed)
11. Unauthorized API access checks (Passed)
12. End-to-end alert ingestion & prioritization flow (Passed)

---

## 11. Truth Mode Status Classification
- **Intelligent Alert Prioritization**: **IMPLEMENTED** (Multi-factor risk engine and priority classification active).
- **Risk Score Methodology**: **TRANSPARENT & EXPLAINABLE** (Itemized factor list returned in payload and UI).
- **Hardcoded Scores**: **NONE** (Scores dynamically computed from empirical log & ML telemetry).
