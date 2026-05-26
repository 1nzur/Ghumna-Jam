from functools import wraps

from flask import current_app, flash, redirect, render_template, request, session, url_for

from app.models.base_model import BaseModel
from app.models.database import init_db


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access the homepage.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view


class AuthController:
    def login(self):
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            if not email or not password:
                flash("Please enter your email and password.", "error")
                return render_template("login.html"), 400

            try:
                init_db(current_app)
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
            return redirect(url_for("auth.home"))

        return render_template("login.html")

    def register(self):
        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            if not full_name or not email or not password:
                flash("Please fill in every required field.", "error")
                return render_template("signup.html"), 400

            try:
                init_db(current_app)
                BaseModel.create_user(full_name, email, password)
            except ValueError as exc:
                flash(str(exc), "error")
                return render_template("signup.html"), 400
            except Exception:
                flash("We could not create your account right now.", "error")
                return render_template("signup.html"), 500

            flash("Account created successfully. You can log in now.", "success")
            return redirect(url_for("auth.login"))

        return render_template("signup.html")

    def signup(self):
        return self.register()

    @login_required
    def home(self):
        return render_template("homepage.html", user_name=session.get("user_name"))

    @login_required
    def landpage(self):
        return render_template("homepage.html", user_name=session.get("user_name"))

    def logout(self):
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for("auth.login"))
