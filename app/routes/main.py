from flask import Blueprint, redirect, render_template, session, url_for

from app.db import execute_query

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    destinations = execute_query(
        "SELECT * FROM destinations ORDER BY duration_days, price_per_person"
    )
    return render_template("landpage.html", destinations=destinations)


@main_bp.route("/login")
def old_login():
    return redirect(url_for("auth.login"))


@main_bp.route("/signup")
def old_signup():
    return redirect(url_for("auth.signup"))


@main_bp.route("/edit-profile")
@main_bp.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login", next=url_for("main.profile")))
    return render_template("edit-profile.html")
