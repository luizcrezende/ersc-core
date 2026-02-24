from __future__ import annotations
from typing import Dict, Any

class PolicyEnforcementAgent:
    """"MVP policy gate: approves/denies and tells if human approval is required."""

    def run(self, incident: Dict[str, Any], risk: Dict[str, Any]) -> Dict[str, Any]:
        requested_action = (incident.get("requested_action") or "NONE").upper()
        risk_score = int(risk["result"]["risk_score"])
        risk_category = risk["result"]["risk_category"]

        # Policy rules (MVP):
        # - Any action on HIGH risk requires human approval
        # - RESET_TRIP is allowed if not HIGH risk; otherwise require approval
        # - Any unknown action is denied
        requires_human = (risk_category == "HIGH")
        allowed = True
        reason = "Allowed by MVP policy."

        if requested_action not in {"RESET_TRIP", "ACK_ALARM", "NONE"}:
            allowed = False
            reason = f"Denied: action '{requested_action}' not allowed in MVP."

        if allowed and requires_human:
            reason = "Allowed, but requires explicit human approval due to HIGH risk."

        return {
            "agent": "PolicyEnforcementAgent",
            "result": {
                "requested_action": requested_action,
                "allowed": allowed,
                "requires_human_approval": requires_human,
                "reason": reason
            }
        }
