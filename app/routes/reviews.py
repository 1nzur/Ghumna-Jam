from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from app.db import execute_query

reviews_bp = Blueprint("reviews", __name__)

MIN_REVIEW_BODY_LENGTH = 20
MAX_REVIEW_TITLE_LENGTH = 120


def require_login(next_url):
    if "user_id" not in session:
        flash("Please log in to manage reviews.", "error")
        return redirect(url_for("auth.login", next=next_url))
    return None


def validate_review_form(form):
    raw_rating = form.get("rating", "").strip()
    title = form.get("title", "").strip()
    body = form.get("body", "").strip()

    try:
        rating = int(raw_rating)
    except ValueError:
        return None, title, body, "Please choose a rating from 1 to 5."

    if rating < 1 or rating > 5:
        return None, title, body, "Please choose a rating from 1 to 5."

    if not title:
        return None, title, body, "Review title is required."

    if len(title) > MAX_REVIEW_TITLE_LENGTH:
        return None, title, body, f"Review title must be {MAX_REVIEW_TITLE_LENGTH} characters or fewer."

    if len(body) < MIN_REVIEW_BODY_LENGTH:
        return None, title, body, f"Review details must be at least {MIN_REVIEW_BODY_LENGTH} characters."

    return rating, title, body, None


def get_review_for_user(review_id):
    rows = execute_query(
        """
        SELECT r.*, d.name AS dest_name
        FROM reviews r
        JOIN destinations d ON r.destination_id = d.id
        WHERE r.id = ? AND r.user_id = ?
        """,
        (review_id, session["user_id"]),
    )
    if not rows:
        abort(404)
    return rows[0]


@reviews_bp.route("/destination/<int:dest_id>/reviews", methods=["POST"])
def create_review(dest_id):
    login_redirect = require_login(url_for("bookings.destination_detail", dest_id=dest_id))
    if login_redirect:
        return login_redirect

    destination_rows = execute_query("SELECT id, name FROM destinations WHERE id = ?", (dest_id,))
    if not destination_rows:
        abort(404)

    rating, title, body, error = validate_review_form(request.form)
    if error:
        flash(error, "error")
        return redirect(url_for("bookings.destination_detail", dest_id=dest_id) + "#reviews")

    existing_review = execute_query(
        "SELECT id FROM reviews WHERE user_id = ? AND destination_id = ?",
        (session["user_id"], dest_id),
    )
    if existing_review:
        flash("You have already reviewed this destination. Edit your existing review instead.", "error")
        return redirect(url_for("reviews.my_reviews"))

    execute_query(
        """
        INSERT INTO reviews (user_id, destination_id, rating, title, body, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (session["user_id"], dest_id, rating, title, body, "Published"),
        commit=True,
    )
    flash(f"Thanks for reviewing {destination_rows[0]['name']}.", "success")
    return redirect(url_for("bookings.destination_detail", dest_id=dest_id) + "#reviews")


@reviews_bp.route("/my-reviews")
def my_reviews():
    login_redirect = require_login(url_for("reviews.my_reviews"))
    if login_redirect:
        return login_redirect

    review_rows = execute_query(
        """
        SELECT r.*, d.name AS dest_name, d.image_url AS dest_image, d.difficulty
        FROM reviews r
        JOIN destinations d ON r.destination_id = d.id
        WHERE r.user_id = ?
        ORDER BY r.updated_at DESC, r.created_at DESC
        """,
        (session["user_id"],),
    )
    published_reviews = [review for review in review_rows if review["status"] == "Published"]
    review_stats = {
        "total": len(review_rows),
        "published": len(published_reviews),
        "hidden": len(review_rows) - len(published_reviews),
        "average_rating": (
            sum(review["rating"] for review in published_reviews) / len(published_reviews)
            if published_reviews
            else 0
        ),
    }

    return render_template("reviews.html", reviews=review_rows, stats=review_stats)
