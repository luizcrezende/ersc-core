from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class DiagnosticResult:
    hypotheses: List[str]
    confidence: float
    notes: str

class DiagnosticAgent:
    """"Deterministic diagnostic stub for MVP demo."""

    def run(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        symptoms = set((incident.get("symptoms") or []))
        hypotheses: List[str] = []
        confidence = 0.55

        if "overcurrent_trip" in symptoms:
            hypotheses.append("Possible short-circuit / overload event")
            confidence += 0.15
        if "thermal_alarm" in symptoms:
            hypotheses.append("Thermal stress: ventilation or contact resistance")
            confidence += 0.10

        if not hypotheses:
            hypotheses.append("Insufficient symptoms: require additional telemetry")

        result = DiagnosticResult(
            hypotheses=hypotheses,
            confidence=min(confidence, 0.90),
            notes="MVP stub: rule-based hypotheses derived from symptoms."
        )

        return {
            "agent": "DiagnosticAgent",
            "result": {
                "hypotheses": result.hypotheses,
                "confidence": result.confidence,
                "notes": result.notes
            }
        }
