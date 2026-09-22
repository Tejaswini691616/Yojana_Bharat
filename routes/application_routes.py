# PATH: GovScheme/routes/application_routes.py
from flask import Blueprint, render_template, redirect, url_for, session, flash

from routes.auth_routes import login_required
from models.application_model import (create_application, get_application,
                                       get_applications_for_user, update_application_status)
from models.scheme_model import get_scheme_by_id
from models.user_model import get_user_by_id
from models.notification_model import create_notification
from rpa.application_request import submit_application

application_bp = Blueprint("application", __name__)


@application_bp.route("/applications")
@login_required
def applications_list():
    apps = get_applications_for_user(session["user_id"])
    return render_template("applications/applications.html", applications=apps)


@application_bp.route("/schemes/<scheme_id>/apply", methods=["POST"])
@login_required
def apply_now(scheme_id):
    user = get_user_by_id(session["user_id"])
    scheme = get_scheme_by_id(scheme_id)
    if not scheme:
        flash("Scheme not found.", "warning")
        return redirect(url_for("scheme.schemes_list"))

    application_id = create_application(user["user_id"], scheme_id)
    update_application_status(application_id, "Queued")

    result = submit_application(application_id, user, scheme)
    update_application_status(application_id, result["status"],
                               result.get("application_number"), result.get("remarks"))

    create_notification(user["user_id"], "Application submitted",
                         f"Your application for {scheme['scheme_name']} is now '{result['status']}'.")

    flash(f"Application {result['status']}. Reference: {result.get('application_number') or 'pending'}", "info")
    return redirect(url_for("application.application_details", application_id=application_id))


@application_bp.route("/applications/<int:application_id>")
@login_required
def application_details(application_id):
    app_row = get_application(application_id)
    if not app_row or app_row["user_id"] != session["user_id"]:
        flash("Application not found.", "warning")
        return redirect(url_for("application.applications_list"))
    return render_template("applications/application_details.html", application=app_row)
