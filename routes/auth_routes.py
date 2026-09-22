# PATH: GovScheme/routes/auth_routes.py
from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from models.user_model import create_user, get_user_by_email, verify_password
from models.db import query_one

auth_bp = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login"))
        user = query_one("SELECT is_admin FROM users WHERE user_id = ?", (session["user_id"],))
        if not user or not user["is_admin"]:
            flash("Admin access required.", "danger")
            return redirect(url_for("dashboard.dashboard_home"))
        return view(*args, **kwargs)
    return wrapped


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form = request.form
        if get_user_by_email(form["email"]):
            flash("An account with this email already exists.", "danger")
            return render_template("auth/register.html")

        user_id = create_user({
            "full_name": form.get("full_name"),
            "email": form.get("email"),
            "password": form.get("password"),
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
        session["user_id"] = user_id
        flash("Welcome to SmartGov AI!", "success")
        return redirect(url_for("dashboard.dashboard_home"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = get_user_by_email(email)
        if user and verify_password(user, password):
            session["user_id"] = user["user_id"]
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard.dashboard_home"))
        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
