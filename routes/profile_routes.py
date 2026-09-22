# PATH: GovScheme/routes/profile_routes.py
from flask import Blueprint, render_template, request, session, redirect, url_for, flash

from routes.auth_routes import login_required
from models.user_model import get_user_by_id, update_user_profile
from ai.recommendation_model import get_recommendations

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
@login_required
def profile_view():
    user = get_user_by_id(session["user_id"])
    return render_template("profile/profile.html", user=user)


@profile_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def profile_edit():
    user = get_user_by_id(session["user_id"])
    if request.method == "POST":
        form = request.form
        update_user_profile(session["user_id"], {
            "full_name": form.get("full_name"),
            "phone": form.get("phone"),
            "gender": form.get("gender"),
            "age": int(form["age"]) if form.get("age") else None,
            "state": form.get("state"),
            "district": form.get("district"),
            "education": form.get("education"),
            "occupation": form.get("occupation"),
            "annual_income": int(form["annual_income"]) if form.get("annual_income") else None,
            "caste": form.get("caste"),
            "farmer": form.get("farmer", "No"),
            "student": form.get("student", "No"),
            "disabled": form.get("disabled", "No"),
            "senior_citizen": form.get("senior_citizen", "No"),
            "bpl": form.get("bpl", "No"),
            "widow": form.get("widow", "No"),
            "land_holding_acres": float(form["land_holding_acres"]) if form.get("land_holding_acres") else 0,
        })
        # Re-run eligibility/recommendation using the already-trained model
        # (spec section 62: do NOT retrain the ML model on profile update).
        updated_user = get_user_by_id(session["user_id"])
        get_recommendations(updated_user, top_k=5)
        flash("Profile updated. Your eligibility and recommendations have been refreshed.", "success")
        return redirect(url_for("profile.profile_view"))

    return render_template("profile/profile_edit.html", user=user)
