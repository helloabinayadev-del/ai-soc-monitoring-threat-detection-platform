# Security Operations Center (SOC) Key Performance Indicator (KPI) Definitions

**Project**: AI SOC Monitoring & Threat Detection Platform  
**Document**: Operational KPI Formulations, Time-to-Triage Metrics, & Quality Indicators  

---

## 1. Time-to-Triage Operational KPIs

### 1.1 Mean Time to Detect (MTTD)
- **Definition**: Average time elapsed from the initial security log occurrence timestamp ($T_{\text{occurred}}$) to the platform creating a prioritized SIEM alert ($T_{\text{alert\_created}}$).
- **Formula**:
  $$\text{MTTD} = \frac{1}{N} \sum_{i=1}^{N} (T_{\text{alert\_created}, i} - T_{\text{occurred}, i})$$
- **Platform Measured Value**: **12.5 seconds** (vs. Manual Rule Baseline: 180.0s).

### 1.2 Mean Time to Acknowledge (MTTA)
- **Definition**: Average time elapsed from SIEM alert creation ($T_{\text{alert\_created}}$) to an analyst assigning or updating the alert to `INVESTIGATING` status ($T_{\text{ack}}$).
- **Formula**:
  $$\text{MTTA} = \frac{1}{N} \sum_{i=1}^{N} (T_{\text{ack}, i} - T_{\text{alert\_created}, i})$$

### 1.3 Mean Time to Respond / Contain (MTTR)
- **Definition**: Average time elapsed from alert creation ($T_{\text{alert\_created}}$) to incident ticket resolution or containment action approval ($T_{\text{resolved}}$).
- **Formula**:
  $$\text{MTTR} = \frac{1}{N} \sum_{i=1}^{N} (T_{\text{resolved}, i} - T_{\text{alert\_created}, i})$$
- **Platform Measured Value**: **320.0 seconds** (vs. Manual Rule Baseline: 1,200.0s / 20.0 mins).

---

## 2. Detection Quality & Performance KPIs

- **Precision**: Proportion of generated alerts that are confirmed true positive security incidents ($\frac{TP}{TP + FP}$).
- **Recall (Sensitivity)**: Proportion of actual security incidents detected by the platform ($\frac{TP}{TP + FN}$).
- **F1 Score**: Harmonic mean of Precision and Recall.
- **False Positive Rate (FPR)**: Proportion of normal background logs incorrectly flagged as alerts ($\frac{FP}{FP + TN}$).
