from __future__ import annotations
from typing import Dict, Any

class RiskAssessmentAgent:
    """"Simple risk scoring stub: produces a 0..100 risk score and category."""

    def run(self, incident: Dict[str, Any], diagnostic: Dict[str, Any]) -> Dict[str, Any]:
        asset = incident.get("asset") or {}
        criticality = (asset.get("criticality") or "MEDIUM").upper()
        symptoms = set((incident.get("symptoms") or []))

        score = 35
        if criticality == "HIGH":
            score += 25
        elif criticality == "LOW":
            score -= 10

        if "overcurrent_trip" in symptoms:
            score += 20
        if "thermal_alarm" in symptoms:
            score += 10

        score = max(0, min(score, 100))

        if score >= 75:
            category = "HIGH"
        elif score >= 50:
            category = "MEDIUM"
        else:
            category = "LOW"

        return {
            "agent": "RiskAssessmentAgent",
            "result": {
                "risk_score": score,
                "risk_category": category,
                "policy_hint": "Require approval for HIGH risk or critical actions."
            }
        }
