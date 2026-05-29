from flask import Flask, redirect, session, url_for

from app.models.database import Database, close_db
from app.routes.auth import AuthRoutes


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("../config.py")

    startup_db = Database()
    startup_db.close()

    app.teardown_appcontext(close_db)
    auth_routes = AuthRoutes()
    app.register_blueprint(auth_routes.register())

    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("auth.home"))
        return redirect(url_for("auth.login"))

    return app
