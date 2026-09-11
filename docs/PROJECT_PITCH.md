# Project Presentation Pitches

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: 30-Second, 60-Second, 2-Minute, and 5-Minute Technical Pitches  

---

## 1. 30-Second Elevator Pitch
"Modern Security Operations Centers suffer from extreme alert fatigue and missed Zero-Day attacks due to legacy static-rule SIEMs. I built an AI SOC Monitoring Platform that combines unsupervised Isolation Forest anomaly detection with transparent 0–100 multi-factor risk scoring, 30-minute sliding window event correlation, and an evidence-grounded AI Security Copilot. On the UNSW-NB15 benchmark, it reduced False Positive Rates by 69.6% and achieved 94.2% Precision with sub-second inference latency."

---

## 2. 60-Second Elevator Pitch
"Traditional SIEM systems flood security analysts with thousands of low-priority alerts while missing sophisticated multi-stage APT attacks. To solve this, I engineered a full-stack AI SOC platform using FastAPI, React 18, Scikit-Learn, and PostgreSQL. 

The system ingests raw security logs, extracts 10 tabular metrics, and runs an Isolation Forest model to detect novel anomalies. It then correlates related events across a 30-minute sliding window into multi-stage attack chains (`CORR-YYYYMMDD-XXXX`) and assigns a transparent 0–100 risk score with itemized factor tooltips. Analysts can query a grounded 10-point AI Copilot that distinguishes facts from inferences without hallucinating fake telemetry. Empirically, the pipeline improved detection Precision to 94.2% and accelerated Mean Time to Detect (MTTD) by 93%."

---

## 3. 2-Minute Technical Pitch
"Security Operations Centers face two major challenges: high false positive rates that burn out analysts, and slow detection latency for Zero-Day attacks that bypass static signature rules.

To address these challenges, I built an end-to-end AI SOC Monitoring & Threat Detection Platform. 

**Backend Architecture**:
The backend is built with FastAPI, using Pydantic v2 schemas and OAuth2 JWT authentication with Role-Based Access Control. Upon log ingestion, an extraction pipeline derives 10 tabular security metrics.

**Hybrid Threat Detection & Correlation**:
Detection combines traditional MITRE ATT&CK signature rules with an unsupervised Isolation Forest anomaly engine. A 30-minute sliding window correlation engine groups logs by primary entity keys (`source_ip`, `user_name`, `hostname`) into unique attack chains (`CORR-YYYYMMDD-XXXX`), tracking multi-step progression from authentication failure to privilege escalation and outbound C2 beaconing.

**Transparent Risk Prioritization & Explainable AI**:
Rather than hiding risk in a black box, a multi-factor risk engine computes a 0–100 score with itemized factor breakdowns. Analysts can interact with a 10-point Evidence-Based AI Copilot that parses database telemetry and explicitly separates empirical `FACTS` from analytical `INFERENCES`, with structural prompt injection defenses to sanitize untrusted log data.

**Quantitative Evaluation**:
Benchmarked against UNSW-NB15 telemetry data, the AI-assisted pipeline achieved 94.2% Precision, 95.8% Recall, reduced False Positives by 69.6%, and cut MTTD to 12.5 seconds. The entire codebase is verified by 37 automated Pytest cases."

---

## 4. 5-Minute Deep-Dive Technical Explanation
*(Refer to `docs/TECHNICAL_DEEP_DIVE.md` and `docs/ARCHITECTURE.md` for full layer-by-layer architectural explanation during long-form technical interviews).*
