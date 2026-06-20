from functools import wraps

from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.controllers.ControllerAuth import login_required


class User:
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self._password_hash = generate_password_hash(password)

    def email_exists(self):
        from app.models.base_model import BaseModel
        try:
            return BaseModel.find_user_by_email(self.email) is not None
        except Exception:
            return False

    def save(self):
        from app.models.base_model import BaseModel
        BaseModel.create_user(self.name, self.email, self._password_hash)

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)

    @classmethod
    def from_db(cls, row):
        obj = cls.__new__(cls)
        obj.name = row.get("full_name") or row.get("name", "")
        obj.email = row.get("email", "")
        obj._password_hash = row.get("password_hash", "")
        return obj


class AuthController:
    def __init__(self):
        from app.models.base_model import BaseModel
        self.user_model = BaseModel

    def register(self):
        if request.method == "GET":
            return render_template("register.html")

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")

        user = User(name, email, password)
        if user.email_exists():
            flash("Email already exists.", "danger")
            return redirect(url_for("auth.register"))

        user.save()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("auth.login"))

    def login(self):
        if request.method == "GET":
            return render_template("login.html")

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("login.html")

        row = self.user_model.find_by(email=email)
        if not row:
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        user = User.from_db(row)
        if not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        session["user_id"] = row["id"]
        session["user_name"] = row.get("full_name") or row.get("name", "")
        session["role"] = "admin" if row.get("is_admin") else "user"
        flash("Login successful!", "success")
        return redirect(url_for("auth.home"))

    def logout(self):
        session.clear()
        flash("Logged out successfully.", "success")
        return redirect(url_for("auth.login"))


__all__ = ["AuthController", "User", "login_required"]
