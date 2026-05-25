from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for

from app.models.base_model import BaseModel
from app.models.database import close_db, init_db


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            flash("Please log in to access the homepage.", "error")
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("../config.py")

    app.teardown_appcontext(close_db)

    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("homepage"))
        return redirect(url_for("login"))

    @app.route("/landpage")
    @login_required
    def home():
        return render_template("landpage.html", user_name=session.get("user_name"))

    @app.route("/homepage")
    @login_required
    def homepage():
        return render_template("homepage.html", user_name=session.get("user_name"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            if not email or not password:
                flash("Please enter your email and password.", "error")
                return render_template("login.html"), 400

            try:
                init_db(app)
                user = BaseModel.authenticate_user(email, password)
            except Exception:
                flash("We could not log you in right now.", "error")
                return render_template("login.html"), 500

            if user is None:
                flash("Invalid email or password.", "error")
                return render_template("login.html"), 401

            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]
            flash("Logged in successfully.", "success")
            return redirect(url_for("homepage"))

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for("login"))

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            if not full_name or not email or not password:
                flash("Please fill in every required field.", "error")
                return render_template("signup.html"), 400

            try:
                init_db(app)
                BaseModel.create_user(full_name, email, password)
            except ValueError as exc:
                flash(str(exc), "error")
                return render_template("signup.html"), 400
            except Exception:
                flash("We could not create your account right now.", "error")
                return render_template("signup.html"), 500

            flash("Account created successfully. You can log in now.", "success")
            return redirect(url_for("login"))

        return render_template("signup.html")

    return app
