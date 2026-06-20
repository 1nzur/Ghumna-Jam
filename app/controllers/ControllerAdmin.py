import os
from datetime import datetime
from functools import wraps

from flask import (
    flash, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import generate_password_hash

from app.models.admin_model import AdminModel
from app.models.database import get_db


# ── Auth decorator ────────────────────────────────────────────────────────────

def admin_required(view):
    """Redirect to the admin login page if the current session is not admin."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Admin access required.", "error")
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)
    return wrapped


# ── Controller ────────────────────────────────────────────────────────────────

class AdminController:

    # ── Auth ──────────────────────────────────────────────────────────────────

    def login(self):
        if session.get("is_admin"):
            return redirect(url_for("admin.dashboard"))

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            if not email or not password:
                flash("Email and password are required.", "error")
                return render_template("admin/login.html"), 400

            db = get_db()
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT id, full_name, password_hash, is_admin FROM users WHERE email = %s",
                    (email,),
                )
                user = cursor.fetchone()

            if not user:
                flash("Invalid credentials.", "error")
                return render_template("admin/login.html"), 401

            from werkzeug.security import check_password_hash
            if not check_password_hash(user["password_hash"], password):
                flash("Invalid credentials.", "error")
                return render_template("admin/login.html"), 401

            if not user["is_admin"]:
                flash("You do not have admin privileges.", "error")
                return render_template("admin/login.html"), 403

            session["is_admin"] = True
            session["admin_id"] = user["id"]
            session["admin_name"] = user["full_name"]
            flash(f"Welcome back, {user['full_name']}!", "success")
            return redirect(url_for("admin.dashboard"))

        return render_template("admin/login.html")

    def logout(self):
        session.pop("is_admin", None)
        session.pop("admin_id", None)
        session.pop("admin_name", None)
        flash("Logged out of admin panel.", "success")
        return redirect(url_for("admin.login"))

    # ── First-time setup ──────────────────────────────────────────────────────

    def setup(self):
        """
        One-time endpoint to promote any existing user to admin.
        Disabled once any admin account exists.
        """
        if AdminModel.admin_exists():
            flash("Setup already complete. Please log in.", "info")
            return redirect(url_for("admin.login"))

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            if not email:
                flash("Email is required.", "error")
                return render_template("admin/setup.html")

            db = get_db()
            with db.cursor() as cursor:
                cursor.execute("SELECT id, full_name FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()

            if not user:
                flash("No account found with that email. Register a normal user first.", "error")
                return render_template("admin/setup.html")

            AdminModel.set_user_admin(user["id"], True)
            flash(
                f"{user['full_name']} is now an admin. Please log in.",
                "success",
            )
            return redirect(url_for("admin.login"))

        return render_template("admin/setup.html")

    # ── Dashboard ─────────────────────────────────────────────────────────────

    @admin_required
    def dashboard(self):
        stats = AdminModel.get_dashboard_stats()
        return render_template("admin/dashboard.html", stats=stats)

    # ── Destinations ──────────────────────────────────────────────────────────

    @admin_required
    def destinations(self):
        destinations = AdminModel.get_all_destinations()
        return render_template("admin/destinations.html", destinations=destinations)

    @admin_required
    def destination_new(self):
        return render_template("admin/destination_form.html", destination=None)

    @admin_required
    def destination_create(self):
        data = self._parse_destination_form()
        if data is None:
            return redirect(url_for("admin.destination_new"))
        try:
            AdminModel.create_destination(data)
            flash(f'Destination "{data["name"]}" created successfully.', "success")
        except Exception as exc:
            flash(f"Could not create destination: {exc}", "error")
        return redirect(url_for("admin.destinations"))

    @admin_required
    def destination_edit(self, dest_id):
        destination = AdminModel.get_destination_by_id(dest_id)
        if not destination:
            flash("Destination not found.", "error")
            return redirect(url_for("admin.destinations"))
        return render_template("admin/destination_form.html", destination=destination)

    @admin_required
    def destination_update(self, dest_id):
        data = self._parse_destination_form()
        if data is None:
            return redirect(url_for("admin.destination_edit", dest_id=dest_id))
        try:
            AdminModel.update_destination(dest_id, data)
            flash(f'Destination "{data["name"]}" updated.', "success")
        except Exception as exc:
            flash(f"Could not update destination: {exc}", "error")
        return redirect(url_for("admin.destinations"))

    @admin_required
    def destination_delete(self, dest_id):
        dest = AdminModel.get_destination_by_id(dest_id)
        try:
            AdminModel.delete_destination(dest_id)
            name = dest["name"] if dest else str(dest_id)
            flash(f'Destination "{name}" deleted.', "success")
        except Exception as exc:
            flash(f"Could not delete destination: {exc}", "error")
        return redirect(url_for("admin.destinations"))

    @staticmethod
    def _parse_destination_form():
        """Extract and validate destination fields from a POST form."""
        name = request.form.get("name", "").strip()
        if not name:
            flash("Destination name is required.", "error")
            return None
        try:
            duration = int(request.form.get("duration_days", 0))
            price = float(request.form.get("price_per_person", 0))
            altitude = int(request.form.get("altitude_meters", 0))
        except ValueError:
            flash("Duration, price, and altitude must be numbers.", "error")
            return None

        return {
            "name": name,
            "category": request.form.get("category", "hike"),
            "image_url": request.form.get("image_url", "").strip(),
            "difficulty": request.form.get("difficulty", "Moderate"),
            "duration_days": duration,
            "season": request.form.get("season", "").strip(),
            "description": request.form.get("description", "").strip(),
            "price_per_person": price,
            "altitude_meters": altitude,
            "highlights": request.form.get("highlights", "").strip(),
            "is_active": request.form.get("is_active") == "1",
        }

    # ── Users ─────────────────────────────────────────────────────────────────

    @admin_required
    def users(self):
        users = AdminModel.get_all_users()
        return render_template("admin/users.html", users=users)

    @admin_required
    def user_toggle_admin(self, user_id):
        # Prevent an admin from removing their own privilege
        if user_id == session.get("admin_id"):
            flash("You cannot change your own admin status.", "error")
            return redirect(url_for("admin.users"))
        user = AdminModel.get_user_by_id(user_id)
        if not user:
            flash("User not found.", "error")
            return redirect(url_for("admin.users"))
        new_status = not bool(user["is_admin"])
        AdminModel.set_user_admin(user_id, new_status)
        label = "granted admin" if new_status else "revoked admin from"
        flash(f'Successfully {label} {user["full_name"]}.', "success")
        return redirect(url_for("admin.users"))

    @admin_required
    def user_delete(self, user_id):
        if user_id == session.get("admin_id"):
            flash("You cannot delete your own account.", "error")
            return redirect(url_for("admin.users"))
        user = AdminModel.get_user_by_id(user_id)
        if not user:
            flash("User not found.", "error")
            return redirect(url_for("admin.users"))
        try:
            AdminModel.delete_user(user_id)
            flash(f'User "{user["full_name"]}" deleted.', "success")
        except Exception as exc:
            flash(f"Could not delete user: {exc}", "error")
        return redirect(url_for("admin.users"))

    # ── Reviews ───────────────────────────────────────────────────────────────

    @admin_required
    def reviews(self):
        reviews = AdminModel.get_all_reviews()
        return render_template("admin/reviews.html", reviews=reviews)

    @admin_required
    def review_delete(self, review_id):
        try:
            AdminModel.delete_review(review_id)
            flash("Review removed.", "success")
        except Exception as exc:
            flash(f"Could not delete review: {exc}", "error")
        return redirect(url_for("admin.reviews"))

    # ── Announcements ─────────────────────────────────────────────────────────

    @admin_required
    def announcements(self):
        announcements = AdminModel.get_all_announcements()
        return render_template("admin/announcements.html", announcements=announcements)

    @admin_required
    def announcement_create(self):
        title = request.form.get("title", "").strip()
        message = request.form.get("message", "").strip()
        ann_type = request.form.get("type", "info")
        is_active = request.form.get("is_active") == "1"

        if not title or not message:
            flash("Title and message are required.", "error")
            return redirect(url_for("admin.announcements"))

        AdminModel.create_announcement(
            title, message, ann_type, is_active, session["admin_id"]
        )
        flash(f'Announcement "{title}" created.', "success")
        return redirect(url_for("admin.announcements"))

    @admin_required
    def announcement_edit(self, ann_id):
        ann = AdminModel.get_announcement_by_id(ann_id)
        if not ann:
            flash("Announcement not found.", "error")
            return redirect(url_for("admin.announcements"))
        return render_template("admin/announcement_form.html", ann=ann)

    @admin_required
    def announcement_update(self, ann_id):
        title = request.form.get("title", "").strip()
        message = request.form.get("message", "").strip()
        ann_type = request.form.get("type", "info")
        is_active = request.form.get("is_active") == "1"

        if not title or not message:
            flash("Title and message are required.", "error")
            return redirect(url_for("admin.announcement_edit", ann_id=ann_id))

        AdminModel.update_announcement(ann_id, title, message, ann_type, is_active)
        flash("Announcement updated.", "success")
        return redirect(url_for("admin.announcements"))

    @admin_required
    def announcement_delete(self, ann_id):
        try:
            AdminModel.delete_announcement(ann_id)
            flash("Announcement deleted.", "success")
        except Exception as exc:
            flash(f"Could not delete announcement: {exc}", "error")
        return redirect(url_for("admin.announcements"))

    # ── Homepage Content ──────────────────────────────────────────────────────

    @admin_required
    def homepage_content(self):
        sections = AdminModel.get_all_homepage_sections()
        # Index by key for easy template lookup
        sections_map = {s["section_key"]: s for s in sections}
        # Predefined editable section keys with friendly labels
        section_defs = [
            ("hero", "Hero Banner", "The large heading and tagline on the landing page."),
            ("about", "About Section", "Short intro paragraph about Ghumna Jam."),
            ("features", "Features Highlight", "Text describing key features or services."),
            ("cta", "Call-to-Action", "Bottom banner text encouraging users to sign up or book."),
        ]
        return render_template(
            "admin/homepage_content.html",
            sections_map=sections_map,
            section_defs=section_defs,
        )

    @admin_required
    def homepage_section_update(self, section_key):
        title = request.form.get("title", "").strip()
        subtitle = request.form.get("subtitle", "").strip()
        body = request.form.get("body", "").strip()

        AdminModel.upsert_homepage_section(
            section_key, title, subtitle, body, session["admin_id"]
        )
        flash(f'Section "{section_key}" saved.', "success")
        return redirect(url_for("admin.homepage_content"))

    # ── Site Photos ───────────────────────────────────────────────────────────

    @admin_required
    def photos(self):
        photos = AdminModel.get_all_photos()
        sections = sorted({p["section"] for p in photos} | {"gallery", "hero", "destinations"})
        return render_template("admin/photos.html", photos=photos, sections=sections)

    @admin_required
    def photo_add(self):
        title = request.form.get("title", "").strip()
        image_url = request.form.get("image_url", "").strip()
        section = request.form.get("section", "gallery").strip()

        if not image_url:
            flash("Image URL is required.", "error")
            return redirect(url_for("admin.photos"))

        AdminModel.add_photo(title, image_url, section, session["admin_id"])
        flash("Photo added.", "success")
        return redirect(url_for("admin.photos"))

    @admin_required
    def photo_delete(self, photo_id):
        try:
            AdminModel.delete_photo(photo_id)
            flash("Photo deleted.", "success")
        except Exception as exc:
            flash(f"Could not delete photo: {exc}", "error")
        return redirect(url_for("admin.photos"))

    @admin_required
    def photo_toggle(self, photo_id):
        AdminModel.toggle_photo_active(photo_id)
        return redirect(url_for("admin.photos"))
