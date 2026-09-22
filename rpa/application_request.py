# PATH: GovScheme/rpa/application_request.py
"""
RPA application automation (spec sections 55-59).

RPA_MODE=DEMO (default): runs the built-in DEMO government portal
simulator. All generated application numbers are prefixed "DEMO-" and are
NEVER presented as a real government submission (spec section 12/56).

RPA_MODE=UIPATH: calls a UiPath Orchestrator job via REST (requires a real
Orchestrator + a published process; see rpa/uipath/README.md). This code
path will raise a clear error if Orchestrator isn't reachable rather than
silently falling back to fake success.

Never automates CAPTCHA/OTP/biometric/login-control bypass (spec 56/47).
"""
import random
import string
import time

from config import Config
from models.db import execute


class RPAError(Exception):
    pass


def _generate_demo_reference(scheme_id: str) -> str:
    suffix = "".join(random.choices(string.digits, k=8))
    return f"DEMO-{scheme_id}-{suffix}"


def submit_application(application_id: int, user_row: dict, scheme_row: dict) -> dict:
    """
    Structured input (spec 57): application_id, user info, scheme info.
    Structured output (spec 58): status, application_number, remarks, timestamp.
    """
    rpa_job_id = execute("""
        INSERT INTO rpa_jobs (application_id, status, started_at)
        VALUES (?, 'Running', datetime('now'))
    """, (application_id,))

    try:
        if Config.RPA_MODE.upper() == "UIPATH":
            result = _run_via_uipath_orchestrator(application_id, user_row, scheme_row)
        else:
            result = _run_demo_portal(application_id, user_row, scheme_row)
    except Exception as exc:  # noqa: BLE001 - RPA errors must not crash the app
        result = {
            "status": "Needs Manual Action",
            "application_number": None,
            "remarks": f"RPA automation failed: {exc}",
        }

    execute("""
        UPDATE rpa_jobs SET status = ?, application_number = ?, remarks = ?,
        completed_at = datetime('now') WHERE rpa_job_id = ?
    """, (result["status"], result.get("application_number"), result.get("remarks"), rpa_job_id))

    return result


def _run_demo_portal(application_id, user_row, scheme_row) -> dict:
    """
    Simulates: Open portal -> Navigate -> Enter repetitive info ->
    Upload permitted documents -> Submit -> Read reference number.
    This never touches a real website; it's an in-process simulator so
    the demo works with zero external dependencies.
    """
    time.sleep(0.2)  # simulate navigation
    if not user_row.get("full_name") or not user_row.get("annual_income"):
        return {
            "status": "Needs Manual Action",
            "application_number": None,
            "remarks": "Required profile fields missing for demo submission (name/income).",
        }
    reference = _generate_demo_reference(scheme_row["scheme_id"])
    return {
        "status": "Completed",
        "application_number": reference,
        "remarks": "Simulated submission via SmartGov AI DEMO government portal. "
                   "This is NOT a real government application. Verify with the "
                   "official source before relying on this reference number.",
    }


def _run_via_uipath_orchestrator(application_id, user_row, scheme_row) -> dict:
    if not Config.UIPATH_ORCHESTRATOR_URL:
        raise RPAError("UIPATH_ORCHESTRATOR_URL is not configured in .env.")
    # Real integration point - requires `requests` and a published UiPath
    # process. Left unimplemented (no Orchestrator instance in this
    # environment); wire this up against your own Orchestrator tenant:
    #
    # import requests
    # token = _get_orchestrator_token()
    # resp = requests.post(f"{Config.UIPATH_ORCHESTRATOR_URL}/odata/Jobs/UiPath.Server...",
    #                       headers={"Authorization": f"Bearer {token}"},
    #                       json={"startInfo": {"ReleaseKey": "...", "InputArguments": ...}})
    # ...poll job status, then return real status/application_number...
    raise RPAError("UiPath Orchestrator integration is not wired up in this prototype. "
                   "Set RPA_MODE=DEMO, or implement _run_via_uipath_orchestrator() "
                   "against your Orchestrator tenant.")
