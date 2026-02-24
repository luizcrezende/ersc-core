from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict

from src.agents.diagnostic_agent import DiagnosticAgent
from src.agents.risk_agent import RiskAssessmentAgent
from src.agents.policy_agent import PolicyEnforcementAgent
from src.agents.execution_agent import ExecutionAgent

AUDIT_LOG = Path("audit.log")

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def audit_write(event: Dict[str, Any]) -> None:
    line = json.dumps(event, ensure_ascii=False)
    AUDIT_LOG.write_text("", encoding="utf-8") if not AUDIT_LOG.exists() else None
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python src/orchestration/orchestrator.py demo/sample_incident.json")
        return 2

    incident_path = Path(sys.argv[1])
    if not incident_path.exists():
        print(f"ERROR: incident file not found: {incident_path}")
        return 2

    incident = json.loads(incident_path.read_text(encoding="utf-8"))

    # Human approval flag (MVP): pass --approve to simulate approval
    approved_by_human = ("--approve" in sys.argv)

    run_id = f"run-{int(time.time())}"
    audit_write({
        "ts": utc_now_iso(),
        "run_id": run_id,
        "event": "RUN_START",
        "incident_id": incident.get("incident_id"),
        "approved_by_human": approved_by_human
    })

    diagnostic = DiagnosticAgent().run(incident)
    audit_write({"ts": utc_now_iso(), "run_id": run_id, "event": "DIAGNOSTIC", **diagnostic})

    risk = RiskAssessmentAgent().run(incident, diagnostic)
    audit_write({"ts": utc_now_iso(), "run_id": run_id, "event": "RISK", **risk})

    policy = PolicyEnforcementAgent().run(incident, risk)
    audit_write({"ts": utc_now_iso(), "run_id": run_id, "event": "POLICY", **policy})

    execution = ExecutionAgent().run(incident, policy, approved_by_human=approved_by_human)
    audit_write({"ts": utc_now_iso(), "run_id": run_id, "event": "EXECUTION", **execution})

    audit_write({
        "ts": utc_now_iso(),
        "run_id": run_id,
        "event": "RUN_END",
        "status": "OK"
    })

    # Console summary (hackathon-friendly)
    print("ERSC Core MVP — Run Summary")
    print(f"- run_id: {run_id}")
    print(f"- incident_id: {incident.get('incident_id')}")
    print(f"- risk_score: {risk['result']['risk_score']} ({risk['result']['risk_category']})")
    print(f"- policy_allowed: {policy['result']['allowed']}")
    print(f"- requires_human_approval: {policy['result']['requires_human_approval']}")
    print(f"- approved_by_human: {approved_by_human}")
    print(f"- executed: {execution['result']['executed']} (simulation_only={execution['result']['simulation_only']})")
    print(f"- audit_log: {AUDIT_LOG.resolve()}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
