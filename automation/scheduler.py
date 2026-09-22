# PATH: GovScheme/automation/scheduler.py
"""
24-hour scheduler (spec section 25) + manual "Run Scheme Update Check Now"
trigger, so an examiner never has to wait 24 hours (also spec section 25).

Pipeline: fetch_candidate_schemes() -> validate_scheme() -> detect_change()
-> store in `schemes` + `scheme_updates` -> re-evaluate affected users'
eligibility/recommendations -> create notifications (spec section 26).
"""
from apscheduler.schedulers.background import BackgroundScheduler

from automation.scheme_scraper import fetch_candidate_schemes
from automation.scheme_validator import validate_scheme
from automation.change_detector import detect_change
from models.db import execute, query
from models.notification_model import create_notification
from ai.recommendation_model import get_eligible_schemes_with_explanations
from models.user_model import get_user_by_id

_scheduler = None


def run_scheme_update_check() -> dict:
    """Runs the full discovery pipeline once. Returns a summary dict."""
    candidates = fetch_candidate_schemes()
    summary = {"checked": 0, "new": 0, "updated": 0, "unchanged": 0, "invalid": 0}

    for candidate in candidates:
        summary["checked"] += 1
        is_valid, errors = validate_scheme(candidate)
        if not is_valid:
            summary["invalid"] += 1
            execute("""INSERT INTO automation_logs (job_name, status, details)
                       VALUES ('scheme_update_check', 'INVALID', ?)""", (str(errors),))
            continue

        change = detect_change(candidate)
        change_type = change["change_type"]
        summary[change_type.lower()] += 1

        execute("""INSERT INTO scheme_updates (scheme_id, source, change_type, old_value, new_value)
                   VALUES (?, ?, ?, ?, ?)""",
                (candidate["scheme_id"], "mock_official_feed.json", change_type,
                 change["old_value"], change["new_value"]))

        if change_type in ("NEW", "UPDATED"):
            _upsert_scheme(candidate)
            _notify_affected_users(candidate["scheme_id"], change_type)

    execute("""INSERT INTO automation_logs (job_name, status, details)
               VALUES ('scheme_update_check', 'COMPLETED', ?)""", (str(summary),))
    return summary


def _upsert_scheme(candidate: dict):
    execute("""
        INSERT INTO schemes (scheme_id, scheme_name, category, eligibility,
            min_age, max_age, income_limit, caste_requirement,
            last_checked, last_updated, verification_status, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'),
                'Candidate - pending admin review', 'Active')
        ON CONFLICT(scheme_id) DO UPDATE SET
            scheme_name=excluded.scheme_name,
            category=excluded.category,
            eligibility=excluded.eligibility,
            min_age=excluded.min_age,
            max_age=excluded.max_age,
            income_limit=excluded.income_limit,
            caste_requirement=excluded.caste_requirement,
            last_checked=datetime('now'),
            last_updated=datetime('now'),
            verification_status='Candidate - pending admin review'
    """, (candidate["scheme_id"], candidate["scheme_name"], candidate.get("category"),
          candidate.get("eligibility"), candidate.get("min_age"), candidate.get("max_age"),
          candidate.get("income_limit"), candidate.get("caste_requirement")))


def _notify_affected_users(scheme_id: str, change_type: str):
    """Re-evaluates all registered users against this scheme and notifies
    those who are now potentially eligible (spec section 26)."""
    users = query("SELECT * FROM users")
    for user in users:
        eligible = get_eligible_schemes_with_explanations(user)
        if any(e["scheme"]["scheme_id"] == scheme_id for e in eligible):
            title = f"{change_type.title()} scheme may match your profile"
            message = f"Scheme {scheme_id} was just marked {change_type}. Check your recommendations."
            create_notification(user["user_id"], title, message)


def init_scheduler(app):
    global _scheduler
    if _scheduler is not None:
        return _scheduler
    interval_hours = app.config.get("SCHEME_UPDATE_INTERVAL_HOURS", 24)
    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.add_job(run_scheme_update_check, "interval", hours=interval_hours,
                        id="scheme_update_check", replace_existing=True)
    _scheduler.start()
    return _scheduler
