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
