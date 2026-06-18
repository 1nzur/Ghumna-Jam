from flask import Blueprint, redirect, render_template, session, url_for

from app.db import execute_query

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    destinations = execute_query(
        "SELECT * FROM destinations ORDER BY duration_days, price_per_person"
    )
    review_rows = execute_query(
        """
        SELECT destination_id, COUNT(*) AS review_count, AVG(rating) AS average_rating
        FROM reviews
        WHERE status = 'Published'
        GROUP BY destination_id
        """
    )
    review_summary = {
        row["destination_id"]: {
            "count": row["review_count"],
            "average": float(row["average_rating"]),
        }
        for row in review_rows
    }
    return render_template(
        "landpage.html",
        destinations=destinations,
        review_summary=review_summary,
    )


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
