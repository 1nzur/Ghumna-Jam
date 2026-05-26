from flask import Flask, redirect, session, url_for

from app.models.database import Database, close_db
from app.routes.auth import AuthRoute


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("../config.py")

    startup_db = Database()
    startup_db.close()

    app.teardown_appcontext(close_db)
    app.register_blueprint(AuthRoute().bp)

    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("auth.home"))
        return redirect(url_for("auth.login"))

    return app
