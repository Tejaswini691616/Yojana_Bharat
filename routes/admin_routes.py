# PATH: GovScheme/routes/admin_routes.py
import json
import os

from flask import Blueprint, render_template, redirect, url_for, flash

from routes.auth_routes import admin_required
from models.db import query
from automation.scheduler import run_scheme_update_check
from config import Config

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
@admin_required
def admin_home():
    stats = {
        "total_citizens": query("SELECT COUNT(*) c FROM users")[0]["c"],
        "total_schemes": query("SELECT COUNT(*) c FROM schemes")[0]["c"],
        "total_applications": query("SELECT COUNT(*) c FROM applications")[0]["c"],
        "total_notifications": query("SELECT COUNT(*) c FROM notifications")[0]["c"],
        "candidate_schemes": query(
            "SELECT COUNT(*) c FROM schemes WHERE verification_status LIKE 'Candidate%'")[0]["c"],
    }
    recent_updates = query("SELECT * FROM scheme_updates ORDER BY checked_at DESC LIMIT 20")
    recent_logs = query("SELECT * FROM automation_logs ORDER BY run_at DESC LIMIT 10")

    ml_metrics = None
    if os.path.exists(Config.ML_METRICS_PATH):
        with open(Config.ML_METRICS_PATH, "r", encoding="utf-8") as f:
            ml_metrics = json.load(f)

    return render_template("admin/admin_dashboard.html", stats=stats,
                            recent_updates=recent_updates, recent_logs=recent_logs,
                            ml_metrics=ml_metrics)


@admin_bp.route("/admin/run-scheme-check", methods=["POST"])
@admin_required
def run_scheme_check():
    summary = run_scheme_update_check()
    flash(f"Scheme update check complete: {summary}", "info")
    return redirect(url_for("admin.admin_home"))


@admin_bp.route("/admin/verify-scheme/<scheme_id>", methods=["POST"])
@admin_required
def verify_scheme(scheme_id):
    from models.db import execute
    execute("UPDATE schemes SET verification_status = 'Verified (admin reviewed)' WHERE scheme_id = ?",
            (scheme_id,))
    flash(f"Scheme {scheme_id} marked as verified.", "success")
    return redirect(url_for("admin.admin_home"))
