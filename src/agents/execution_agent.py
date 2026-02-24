from __future__ import annotations
from typing import Dict, Any

class ExecutionAgent:
    """"MVP execution stub: does not touch real systems; simulates execution."""

    def run(self, incident: Dict[str, Any], policy: Dict[str, Any], approved_by_human: bool) -> Dict[str, Any]:
        requested_action = policy["result"]["requested_action"]
        allowed = bool(policy["result"]["allowed"])
        requires_human = bool(policy["result"]["requires_human_approval"])

        executed = False
        execution_note = "No execution performed."

        if not allowed:
            execution_note = "Execution blocked: policy denied."
        elif requires_human and not approved_by_human:
            execution_note = "Execution blocked: missing human approval."
        else:
            executed = True
            execution_note = f"Simulated execution completed for action: {requested_action}"

        return {
            "agent": "ExecutionAgent",
            "result": {
                "executed": executed,
                "simulation_only": True,
                "note": execution_note
            }
        }
