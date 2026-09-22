# PATH: GovScheme/routes/scheme_routes.py
from flask import Blueprint, render_template, request, session, redirect, url_for, flash

from routes.auth_routes import login_required
from models.scheme_model import search_schemes, get_scheme_by_id, get_categories_with_counts
from models.user_model import get_user_by_id
from models.db import query, execute
from ai.eligibility_engine import evaluate_eligibility
from models.user_model import citizen_dict_for_engine
from models.scheme_model import scheme_to_engine_dict

scheme_bp = Blueprint("scheme", __name__)


@scheme_bp.route("/schemes")
@login_required
def schemes_list():
    keyword = request.args.get("q", "")
    category = request.args.get("category", "")
    state = request.args.get("state", "")

    results = search_schemes(keyword=keyword, category=category, state=state)
    categories = get_categories_with_counts()

    user = get_user_by_id(session["user_id"])
    citizen = citizen_dict_for_engine(user)
    for s in results:
        result = evaluate_eligibility(citizen, scheme_to_engine_dict(s))
        s["eligibility_badge"] = "Potentially Eligible" if result.is_eligible else "Not Eligible"

    saved_ids = {r["scheme_id"] for r in query(
        "SELECT scheme_id FROM saved_schemes WHERE user_id = ?", (user["user_id"],))}

    return render_template("schemes/schemes.html", schemes=results, categories=categories,
                            keyword=keyword, category=category, saved_ids=saved_ids)


@scheme_bp.route("/schemes/<scheme_id>")
@login_required
def scheme_details(scheme_id):
    scheme = get_scheme_by_id(scheme_id)
    if not scheme:
        flash("Scheme not found.", "warning")
        return redirect(url_for("scheme.schemes_list"))

    user = get_user_by_id(session["user_id"])
    citizen = citizen_dict_for_engine(user)
    result = evaluate_eligibility(citizen, scheme_to_engine_dict(scheme))

    is_saved = query("SELECT 1 FROM saved_schemes WHERE user_id = ? AND scheme_id = ?",
                      (user["user_id"], scheme_id))

    return render_template("schemes/scheme_details.html", scheme=scheme, result=result,
                            is_saved=bool(is_saved))


@scheme_bp.route("/schemes/<scheme_id>/save", methods=["POST"])
@login_required
def save_scheme(scheme_id):
    execute("INSERT OR IGNORE INTO saved_schemes (user_id, scheme_id) VALUES (?, ?)",
            (session["user_id"], scheme_id))
    flash("Scheme saved.", "success")
    return redirect(request.referrer or url_for("scheme.schemes_list"))


@scheme_bp.route("/schemes/<scheme_id>/unsave", methods=["POST"])
@login_required
def unsave_scheme(scheme_id):
    execute("DELETE FROM saved_schemes WHERE user_id = ? AND scheme_id = ?",
            (session["user_id"], scheme_id))
    flash("Scheme removed from saved list.", "info")
    return redirect(request.referrer or url_for("scheme.schemes_list"))


@scheme_bp.route("/saved-schemes")
@login_required
def saved_schemes_list():
    schemes = query("""
        SELECT s.* FROM saved_schemes ss JOIN schemes s ON ss.scheme_id = s.scheme_id
        WHERE ss.user_id = ? ORDER BY ss.saved_date DESC
    """, (session["user_id"],))
    return render_template("schemes/saved_schemes.html", schemes=schemes)
