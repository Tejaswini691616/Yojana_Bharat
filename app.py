# PATH: GovScheme/app.py
import os
from flask import Flask, session, redirect, url_for

from config import Config
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.scheme_routes import scheme_bp
from routes.application_routes import application_bp
from routes.profile_routes import profile_bp
from routes.notification_routes import notification_bp
from routes.admin_routes import admin_bp
from routes.chatbot_routes import chatbot_bp
from models.notification_model import unread_count


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(scheme_bp)
    app.register_blueprint(application_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chatbot_bp)

    @app.context_processor
    def inject_globals():
        user_id = session.get("user_id")
        notif_count = unread_count(user_id) if user_id else 0
        return {"disclaimer": Config.DISCLAIMER, "unread_notifications": notif_count}

    @app.route("/")
    def index():
        if session.get("user_id"):
            return redirect(url_for("dashboard.dashboard_home"))
        return redirect(url_for("auth.login"))

    # Only start the 24-hour scheduler in the reloader's main process
    # (avoids duplicate jobs when Flask debug reloader spawns a subprocess).
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true" and not app.config["DEBUG"]:
        from automation.scheduler import init_scheduler
        init_scheduler(app)
    elif os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        from automation.scheduler import init_scheduler
        init_scheduler(app)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=5000)
