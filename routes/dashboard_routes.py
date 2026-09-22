# PATH: GovScheme/routes/dashboard_routes.py
from flask import Blueprint, render_template, session

from routes.auth_routes import login_required
from models.user_model import get_user_by_id
from models.scheme_model import get_categories_with_counts
from models.db import query
from ai.recommendation_model import get_recommendations

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard_home():
    user = get_user_by_id(session["user_id"])
    categories = get_categories_with_counts()
    recommendations = get_recommendations(user, top_k=5)

    saved = query("""
        SELECT s.* FROM saved_schemes ss JOIN schemes s ON ss.scheme_id = s.scheme_id
        WHERE ss.user_id = ? ORDER BY ss.saved_date DESC LIMIT 6
    """, (user["user_id"],))
    saved_ids = {s["scheme_id"] for s in saved}

    total_schemes = query("SELECT COUNT(*) as c FROM schemes")[0]["c"]

    return render_template("dashboard/dashboard.html",
                            user=user, categories=categories,
                            recommendations=recommendations,
                            saved_schemes=saved, saved_ids=saved_ids,
                            total_schemes=total_schemes)
