import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

import azure.functions as func
from azure.cosmos import CosmosClient

SEVERITY_ALLOWED = {"S0", "S1", "S2", "S3", "S4"}

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DATABASE = os.getenv("COSMOS_DATABASE", "ersc-core-db")
COSMOS_AUDIT_CONTAINER = os.getenv("COSMOS_AUDIT_CONTAINER", "audit-log")
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
REGION = os.getenv("REGION", "brazilsouth")

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def make_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    suffix = uuid.uuid4().hex[:4]
    return f"run_{stamp}_{suffix}"

def bad_request(message: str, details: Dict[str, Any] | None = None) -> func.HttpResponse:
    payload = {"error": {"message": message, "details": details or {}}}
    return func.HttpResponse(json.dumps(payload), status_code=400, mimetype="application/json")

def ok(payload: Dict[str, Any]) -> func.HttpResponse:
    return func.HttpResponse(json.dumps(payload), status_code=200, mimetype="application/json")

def validate_incident(body: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    if not isinstance(body, dict):
        return False, "Body must be a JSON object.", {}

    incident = body.get("incident")
    context = body.get("context", {})

    if not isinstance(incident, dict):
        return False, "Missing or invalid 'incident' object.", {}

    incident_id = incident.get("incidentId")
    severity = incident.get("severity")

    if not incident_id or not isinstance(incident_id, str):
        return False, "Missing or invalid 'incident.incidentId'.", {}

    if not severity or not isinstance(severity, str) or severity not in SEVERITY_ALLOWED:
        return False, "Invalid 'incident.severity'. Allowed: S0, S1, S2, S3, S4.", {
            "received": severity,
            "allowed": sorted(list(SEVERITY_ALLOWED)),
        }

    tenant_id = context.get("tenantId")
    if not tenant_id or not isinstance(tenant_id, str):
        return False, "Missing or invalid 'context.tenantId'.", {}

    normalized = {
        "incident": incident,
        "context": {
            "tenantId": tenant_id,
            "environment": context.get("environment", ENVIRONMENT),
            "runMode": context.get("runMode", "SIMULATED"),
            "policyProfile": context.get("policyProfile", "industrial-default"),
            "priority": context.get("priority", "HIGH"),
        },
    }

    return True, "", normalized

def get_cosmos_container():
    if not COSMOS_ENDPOINT or not COSMOS_KEY:
        raise RuntimeError("COSMOS_ENDPOINT/COSMOS_KEY not configured.")
    client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)
    db = client.get_database_client(COSMOS_DATABASE)
    return db.get_container_client(COSMOS_AUDIT_CONTAINER)

@app.route(route="incident", methods=["POST"])
def incident(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except ValueError:
        return bad_request("Invalid JSON body.")

    is_valid, err, normalized = validate_incident(body)
    if not is_valid:
        return bad_request(err, normalized if isinstance(normalized, dict) else None)

    run_id = make_run_id()
    ts = utc_now_iso()

    incident_obj = normalized["incident"]
    ctx = normalized["context"]

    event = {
        "id": f"evt_{uuid.uuid4().hex[:12]}",
        "runId": run_id,
        "partitionKey": run_id,
        "ts": ts,
        "seq": 1,
        "stage": "RUN_START",
        "eventType": "RUN_STARTED",
        "tenantId": ctx["tenantId"],
        "environment": ctx["environment"],
        "region": REGION,
        "severity": incident_obj.get("severity"),
        "actor": {"type": "SYSTEM", "id": "orchestrator"},
        "policy": {"profile": ctx["policyProfile"], "decision": None},
        "data": {
            "incidentId": incident_obj.get("incidentId"),
            "title": incident_obj.get("title"),
            "summary": incident_obj.get("summary"),
            "category": incident_obj.get("category"),
            "detectedAt": incident_obj.get("detectedAt"),
            "source": incident_obj.get("source"),
            "constraints": incident_obj.get("constraints", {})
        }
    }

    try:
        container = get_cosmos_container()
        container.create_item(body=event)
    except Exception as ex:
        return func.HttpResponse(
            json.dumps({
                "error": {
                    "message": "Failed to write audit event.",
                    "runId": run_id,
                    "details": str(ex)
                }
            }),
            status_code=500,
            mimetype="application/json"
        )

    response = {
        "run": {
            "runId": run_id,
            "createdAt": ts,
            "tenantId": ctx["tenantId"],
            "environment": ctx["environment"],
            "region": REGION,
            "mode": ctx["runMode"],
            "status": "OK",
            "stage": "RUN_START",
            "correlationId": incident_obj.get("incidentId")
        },
        "audit": {
            "auditRunPartitionKey": run_id,
            "eventsWritten": 1,
            "cosmos": {
                "database": COSMOS_DATABASE,
                "container": COSMOS_AUDIT_CONTAINER
            }
        },
        "links": {
            "runStatus": f"/api/run/{run_id}"
        }
    }

    return ok(response)
