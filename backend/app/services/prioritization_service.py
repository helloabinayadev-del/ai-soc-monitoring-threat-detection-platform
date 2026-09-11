from typing import Dict, Any, List, Optional

class IntelligentAlertPrioritizationService:
    """
    Transparent, explainable risk calculation & alert prioritization engine (0 - 100 scale).
    Combines:
    - Base event severity
    - Scikit-learn ML anomaly score
    - Event frequency & repetition
    - Asset criticality weight
    - Threat intelligence match score
    - Multi-stage event correlation strength
    - Analyst feedback tuning
    """

    SEVERITY_BASE_SCORES = {
        "INFORMATIONAL": 10.0,
        "LOW": 25.0,
        "MEDIUM": 50.0,
        "HIGH": 75.0,
        "CRITICAL": 92.0
    }

    ASSET_CRITICALITY_MULTIPLIERS = {
        "DC-PRIMARY-01": 1.30,
        "SRV-APP-PROD01": 1.25,
        "PROD-DB-01": 1.30,
        "FIREWALL-EDGE": 1.20,
        "WKSTN-FIN-02": 1.10,
        "WKSTN-FIN-09": 1.10,
        "WKSTN-HR-09": 1.05,
    }

    def calculate_risk(
        self,
        severity: str,
        anomaly_score: float = 0.0,
        matched_rule: Optional[Dict[str, Any]] = None,
        source_ip: Optional[str] = None,
        affected_asset: Optional[str] = None,
        threat_intel_match: bool = False,
        correlated_event_count: int = 1,
        frequency_count: int = 1,
        analyst_feedback_bias: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates risk score (0-100) and priority rank (LOW, MEDIUM, HIGH, CRITICAL).
        Returns risk score, priority, and explicit contributing factors breakdown list.
        """
        factors = []
        base_sev = severity.upper() if severity else "MEDIUM"
        base_score = self.SEVERITY_BASE_SCORES.get(base_sev, 50.0)

        if matched_rule and "risk_score" in matched_rule:
            rule_score = float(matched_rule["risk_score"])
            factors.append({
                "factor": f"Triggered Detection Rule: {matched_rule.get('title', 'Security Rule')}",
                "contribution": round(rule_score * 0.5, 2)
            })
            current_score = rule_score * 0.5
        else:
            factors.append({
                "factor": f"Base Event Severity ({base_sev})",
                "contribution": round(base_score * 0.5, 2)
            })
            current_score = base_score * 0.5

        # 2. ML Anomaly Score (Isolation Forest contribution)
        if anomaly_score > 0:
            ml_contrib = anomaly_score * 0.5
            factors.append({
                "factor": f"Isolation Forest ML Anomaly Score ({round(anomaly_score, 1)}/100)",
                "contribution": round(ml_contrib, 2)
            })
            current_score += ml_contrib

        # 3. Frequency & Repetition Burst
        if frequency_count > 1:
            freq_contrib = min(15.0, (frequency_count - 1) * 3.5)
            factors.append({
                "factor": f"Repeated Event Burst ({frequency_count} instances observed)",
                "contribution": round(freq_contrib, 2)
            })
            current_score += freq_contrib

        # 4. Asset Criticality Multiplier
        asset_name = affected_asset or "Unknown Workstation"
        multiplier = self.ASSET_CRITICALITY_MULTIPLIERS.get(asset_name, 1.0)
        if multiplier > 1.0:
            asset_contrib = (multiplier - 1.0) * current_score
            factors.append({
                "factor": f"High Asset Criticality ({asset_name} - {int((multiplier-1.0)*100)}% weight)",
                "contribution": round(asset_contrib, 2)
            })
            current_score *= multiplier

        # 5. Threat Intelligence Match
        if threat_intel_match:
            factors.append({
                "factor": "Threat Intelligence Known Malicious Match",
                "contribution": 20.0
            })
            current_score += 20.0

        # 6. Event Correlation Strength
        if correlated_event_count > 1:
            corr_contrib = min(25.0, (correlated_event_count - 1) * 6.0)
            factors.append({
                "factor": f"Correlated Attack Chain ({correlated_event_count} related security events)",
                "contribution": round(corr_contrib, 2)
            })
            current_score += corr_contrib

        # 7. Analyst Feedback Tuning
        if analyst_feedback_bias != 0.0:
            factors.append({
                "factor": "Analyst Feedback Calibration",
                "contribution": round(analyst_feedback_bias, 2)
            })
            current_score += analyst_feedback_bias

        # Clamp final score (0 - 100)
        final_risk_score = max(0.0, min(100.0, round(current_score, 1)))

        # Determine Priority
        if final_risk_score >= 85.0:
            priority = "CRITICAL"
        elif final_risk_score >= 65.0:
            priority = "HIGH"
        elif final_risk_score >= 40.0:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        return {
            "risk_score": final_risk_score,
            "priority": priority,
            "contributing_factors": factors,
            "calculation_methodology": "Transparent Multi-Factor Risk Calculation Engine (ML Anomaly + Rule Severity + Correlation + Asset Weight + Threat Intel)"
        }

prioritization_service = IntelligentAlertPrioritizationService()
