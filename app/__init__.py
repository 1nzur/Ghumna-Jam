<<<<<<< HEAD
from flask import Flask, redirect, session, url_for
from app.models.database import Database, close_db
from app.routes.auth import AuthRoutes
=======
from flask import Flask

from app.config import Config
from app.db import init_db
from app.routes.auth import auth_bp
from app.routes.bookings import bookings_bp
from app.routes.reviews import reviews_bp
>>>>>>> 28f10469f5bcc5a4b8bb22c4fcbaf984bdfb08e7


def create_app(config_object=Config):
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config.from_object(config_object)

    with app.app_context():
        init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(reviews_bp)

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app
