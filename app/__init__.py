from flask import Flask, redirect, session, url_for

from app.models.database import Database, close_db, init_db
from app.routes.auth import AuthRoutes
from app.routes.admin import AdminRoutes


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("../config.py")

    startup_db = Database()
    startup_db.close()
    init_db(app)

    app.teardown_appcontext(close_db)

    auth_routes = AuthRoutes()
    app.register_blueprint(auth_routes.register())

    admin_routes = AdminRoutes()
    app.register_blueprint(admin_routes.register())

    @app.context_processor
    def inject_notifications():
        if "user_id" not in session:
            return {"unread_count": 0, "recent_notifications": [], "site_announcements": []}
        try:
            from app.models.base_model import BaseModel
            from app.models.admin_model import AdminModel
            count = BaseModel.get_unread_notification_count(session["user_id"])
            notifs = BaseModel.get_notifications(session["user_id"], limit=8)
            announcements = AdminModel.get_active_announcements()
        except Exception:
            count, notifs, announcements = 0, [], []
        return {
            "unread_count": count,
            "recent_notifications": notifs,
            "site_announcements": announcements,
        }

    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("auth.home"))
        return redirect(url_for("auth.login"))

    return app
