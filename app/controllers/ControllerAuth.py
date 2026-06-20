import os
import re
from datetime import datetime
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
    EXCHANGE_RATE = 134.0

    @staticmethod
    def _is_strong_password(password):
        return (
            len(password) >= 8
            and re.search(r"[A-Z]", password)
            and re.search(r"\d", password)
            and re.search(r"[!@#$%^&*(),.?\":{}|<>~`_\-\\\[\];'\/+=]", password)
        )

    @staticmethod
    def _is_token_valid(token):
        return BaseModel.get_user_by_reset_token(token)

    def _sample_destination(self, dest_id=1):
        """Fallback single destination used when the DB row cannot be found."""
        dests = self._sample_destinations()
        match = next((d for d in dests if d["id"] == dest_id), None)
        return match or dests[0]

    def _sample_destinations(self):
        """
        Return destinations from the database.
        Falls back to an empty list on DB error (startup race condition guard).
        """
        try:
            from app.models.admin_model import AdminModel
            rows = AdminModel.get_active_destinations()
            if rows:
                # Ensure price_per_person is a plain float for template arithmetic
                return [dict(r, price_per_person=float(r["price_per_person"])) for r in rows]
        except Exception:
            pass
        # Empty list; the DB hasn't been seeded yet or connection failed
        return []

    def _hotel_options(self, dest_id):
        hotels_by_destination = {
            1: [
                {
                    "name": "Everest View Lodge",
                    "location": "Namche Bazaar",
                    "style": "Mountain lodge",
                    "price_per_night": 8500,
                    "perk": "Panoramic Everest sunrise views",
                },
                {
                    "name": "Sherpa Heritage Inn",
                    "location": "Khumjung",
                    "style": "Family-run inn",
                    "price_per_night": 6200,
                    "perk": "Traditional Sherpa meals",
                },
                {
                    "name": "Base Camp Retreat",
                    "location": "Lobuche",
                    "style": "High-altitude lodge",
                    "price_per_night": 7800,
                    "perk": "Warm dining hall and oxygen support",
                },
                {
                    "name": "Yak & Yeti Trail House",
                    "location": "Phakding",
                    "style": "Trail guesthouse",
                    "price_per_night": 4800,
                    "perk": "Riverside rooms near the Dudh Koshi",
                },
            ],
            2: [
                {
                    "name": "Annapurna Alpine Lodge",
                    "location": "Manang",
                    "style": "Alpine lodge",
                    "price_per_night": 7200,
                    "perk": "Acclimatization-day comfort",
                },
                {
                    "name": "Thorong Pass Tea House",
                    "location": "Thorong Phedi",
                    "style": "Tea house",
                    "price_per_night": 5600,
                    "perk": "Closest rest before the pass",
                },
                {
                    "name": "Marshyangdi River Stay",
                    "location": "Chame",
                    "style": "Riverside hotel",
                    "price_per_night": 5100,
                    "perk": "Hot showers and valley views",
                },
                {
                    "name": "Apple Orchard Guesthouse",
                    "location": "Braga",
                    "style": "Village guesthouse",
                    "price_per_night": 4600,
                    "perk": "Quiet rooms near old monasteries",
                },
            ],
            3: [
                {
                    "name": "Langtang Glacier Lodge",
                    "location": "Kyanjin Gompa",
                    "style": "Glacier-view lodge",
                    "price_per_night": 5800,
                    "perk": "Views toward Langtang Lirung",
                },
                {
                    "name": "Tamang Heritage Stay",
                    "location": "Langtang Village",
                    "style": "Cultural homestay",
                    "price_per_night": 4300,
                    "perk": "Local Tamang hospitality",
                },
                {
                    "name": "Rhododendron Trail Inn",
                    "location": "Lama Hotel",
                    "style": "Forest inn",
                    "price_per_night": 3900,
                    "perk": "Peaceful forest stopover",
                },
                {
                    "name": "Valley View Guesthouse",
                    "location": "Syabrubesi",
                    "style": "Comfort guesthouse",
                    "price_per_night": 4100,
                    "perk": "Easy first-night access",
                },
            ],
        }

        return hotels_by_destination.get(dest_id, hotels_by_destination[1])

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
            session["profile_picture_url"] = user.get("profile_picture_url")
            # Persist admin flag so admin_required decorator works after login
            if user.get("is_admin"):
                session["is_admin"] = True
                session["admin_id"] = user["id"]
                session["admin_name"] = user["full_name"]
            flash("Logged in successfully.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("auth.home"))

        return render_template("login.html")

    def register(self):
        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            terms_accepted = request.form.get("terms_accepted")

            if not full_name or not email or not password:
                flash("Please fill in every required field.", "error")
                return render_template("signup.html"), 400

            if terms_accepted != "accepted":
                flash("Please review and accept the Terms & Conditions before creating an account.", "error")
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

    def terms(self):
        return render_template("terms.html")

    @login_required
    def home(self):
        from app.models.admin_model import AdminModel

        def _section(key):
            """Fetch one homepage section dict, or empty dict if not set yet."""
            try:
                row = AdminModel.get_homepage_section(key)
                return row or {}
            except Exception:
                return {}

        def _photos(section):
            try:
                return AdminModel.get_active_photos_by_section(section)
            except Exception:
                return []

        return render_template(
            "landpage.html",
            destinations=self._sample_destinations(),
            user_name=session.get("user_name"),
            # Homepage content sections from DB (admins edit these)
            hero=_section("hero"),
            about=_section("about"),
            features=_section("features"),
            cta=_section("cta"),
            # Photos from DB grouped by their section name
            gallery_photos=_photos("gallery"),
            hero_photos=_photos("hero"),
        )

    @login_required
    def landpage(self):
        return self.home()

    def forgot_password(self):
        email = ""
        submitted_email = ""
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            if not email:
                flash("Please enter your email address.", "error")
                return render_template("forgot_password.html", email=email), 400
            submitted_email = email
            flash("If that email exists, reset instructions will be sent.", "success")
        return render_template(
            "forgot_password.html",
            email=email,
            submitted_email=submitted_email,
        )

    def reset_password(self, token):
        user = self._is_token_valid(token)
        if not user:
            flash("This password reset link is invalid or expired.", "error")
            return redirect(url_for("auth.forgot_password"))

        if request.method == "POST":
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not password or not confirm_password:
                flash("Please enter and confirm your new password.", "error")
                return render_template("reset_password.html", token=token), 400

            if password != confirm_password:
                flash("Passwords do not match.", "error")
                return render_template("reset_password.html", token=token), 400

            if not self._is_strong_password(password):
                flash(
                    "Password must be at least 8 characters and include 1 uppercase letter, 1 number, and 1 special character.",
                    "error",
                )
                return render_template("reset_password.html", token=token), 400

            try:
                init_db(current_app)
                BaseModel.update_password(user["id"], password)
            except Exception:
                flash("We could not reset your password right now.", "error")
                return render_template("reset_password.html", token=token), 500

            flash("Your password has been reset successfully. Please log in.", "success")
            return redirect(url_for("auth.login"))

        return render_template("reset_password.html", token=token)

    @login_required
    def compare_treks(self):
        selected_ids = []
        for raw_id in request.args.getlist("treks"):
            try:
                trek_id = int(raw_id)
            except ValueError:
                continue

            if trek_id not in selected_ids:
                selected_ids.append(trek_id)

        remove_id = request.args.get("remove", type=int)
        if remove_id:
            selected_ids = [trek_id for trek_id in selected_ids if trek_id != remove_id]

        destinations = self._sample_destinations()
        selected_treks = [
            destination
            for destination in destinations
            if destination["id"] in selected_ids
        ]

        return render_template(
            "compare.html",
            destinations=destinations,
            selected_treks=selected_treks,
            selected_ids=[trek["id"] for trek in selected_treks],
        )

    @login_required
    def bookings(self):
        try:
            init_db(current_app)
            bookings = BaseModel.get_bookings_by_user(session["user_id"])
        except Exception:
            bookings = []
        return render_template("bookings.html", bookings=bookings)

    @login_required
    def cancel_booking(self, booking_id):
        try:
            init_db(current_app)
            BaseModel.cancel_booking(session["user_id"], booking_id)
            flash("Booking cancelled successfully.", "success")
        except Exception:
            flash("Could not cancel the booking right now.", "error")
        return redirect(url_for("auth.bookings"))

    def destination_detail(self, dest_id):
        destination = next(
            (dest for dest in self._sample_destinations() if dest["id"] == dest_id),
            self._sample_destination(dest_id),
        )
        init_db(current_app)
        already_logged = False
        average_rating = 0.0
        review_count = 0
        favorite_ids = []
        can_review = False
        user_review = None
        reviews = []
        try:
            avg, cnt = BaseModel.get_destination_rating(dest_id)
            average_rating = avg
            review_count = cnt
            reviews = BaseModel.get_reviews_for_destination(dest_id)
        except Exception:
            pass
        if session.get("user_id"):
            uid = session["user_id"]
            try:
                already_logged = BaseModel.has_logged_trek(uid, destination["name"])
                can_review = BaseModel.can_review_destination(uid, destination["name"])
                user_review = BaseModel.get_user_review_for_dest(uid, dest_id)
                favorite_ids = BaseModel.get_favorite_destination_ids(uid)
            except Exception:
                pass
        return render_template(
            "destination_detail.html",
            destination=destination,
            hotel_options=self._hotel_options(dest_id),
            already_logged=already_logged,
            average_rating=average_rating,
            review_count=review_count,
            favorite_ids=favorite_ids,
            can_review=can_review,
            user_review=user_review,
            reviews=reviews,
            now=datetime.utcnow(),
        )

    @login_required
    def book_trip(self, dest_id):
        destination = next(
            (dest for dest in self._sample_destinations() if dest["id"] == dest_id),
            self._sample_destination(dest_id),
        )
        travelers_count = max(1, min(12, int(request.form.get("travelers_count", 1) or 1)))
        departure_date = request.form.get("departure_date", "Not selected")
        selected_hotel = request.form.get("selected_hotel", "No hotel selected")

        try:
            init_db(current_app)
            BaseModel.create_booking(
                user_id=session["user_id"],
                dest_name=destination["name"],
                dest_image=destination["image_url"],
                status="Confirmed",
                departure_date=departure_date,
                travelers_count=travelers_count,
                duration_days=destination["duration_days"],
                difficulty=destination["difficulty"],
                selected_hotel=selected_hotel,
                total_price=destination["price_per_person"] * travelers_count,
            )
        except Exception:
            flash("We could not confirm your booking right now. Please try again.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))

        flash("Your journey has been added to your bookings.", "success")
        return redirect(url_for("auth.bookings"))

    @login_required
    def edit_profile(self):
        user = BaseModel.get_user_by_id(session["user_id"])
        # Pop the name-change flag set on a previous POST so the template can migrate localStorage
        name_changed_from = session.pop("_name_changed_from", None)

        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            phone_number = request.form.get("phone_number", "").strip()
            date_of_birth = request.form.get("date_of_birth", "").strip() or None
            password = request.form.get("password", "")

            if not full_name or not email:
                flash("Name and email are required.", "error")
                return render_template("edit-profile.html", user=user, name_changed_from=None), 400

            # Keep existing picture unless a new file is uploaded (C1 + C2 fix)
            profile_picture_url = user.get("profile_picture_url") if user else None
            uploaded_file = request.files.get("profile_picture")
            if uploaded_file and uploaded_file.filename:
                ext = os.path.splitext(uploaded_file.filename)[1].lower()
                if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
                    upload_dir = os.path.join(current_app.root_path, "static", "uploads")
                    os.makedirs(upload_dir, exist_ok=True)
                    filename = f"pfp_{session['user_id']}_{int(datetime.utcnow().timestamp())}{ext}"
                    uploaded_file.save(os.path.join(upload_dir, filename))
                    profile_picture_url = url_for("static", filename=f"uploads/{filename}")

            # Track name change so the template can migrate localStorage posts (C3 fix)
            old_name = user["full_name"] if user else None

            try:
                BaseModel.update_user(
                    session["user_id"],
                    full_name,
                    email,
                    phone_number=phone_number or None,
                    date_of_birth=date_of_birth,
                    profile_picture_url=profile_picture_url,
                    password=password or None,
                )
            except ValueError as exc:
                flash(str(exc), "error")
                return render_template("edit-profile.html", user=user, name_changed_from=None), 400
            except Exception:
                flash("We could not update your profile right now.", "error")
                return render_template("edit-profile.html", user=user, name_changed_from=None), 500

            if old_name and old_name != full_name:
                session["_name_changed_from"] = old_name

            session["user_name"] = full_name
            session["profile_picture_url"] = profile_picture_url
            flash("Profile updated successfully.", "success")
            return redirect(url_for("auth.edit_profile"))

        try:
            init_db(current_app)
            earned_rows = BaseModel.get_user_badges(session["user_id"])
            earned_map = {row["badge_slug"]: row["earned_at"] for row in earned_rows}
            stats = BaseModel.get_completed_trek_stats(session["user_id"])
            badge_list = []
            for badge in BaseModel.BADGE_DEFINITIONS:
                slug = badge["slug"]
                current, target = BaseModel.badge_progress(slug, stats)
                badge_list.append({
                    **badge,
                    "is_earned": slug in earned_map,
                    "earned_at": earned_map.get(slug),
                    "progress_current": current,
                    "progress_target": target,
                    "progress_pct": int(current / target * 100) if target else 0,
                })
        except Exception:
            badge_list = []
        return render_template("edit-profile.html", user=user, name_changed_from=name_changed_from, badge_list=badge_list)

    def logout(self):
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for("auth.login"))

    @login_required
    def tracking(self):
        return render_template("tracking.html")

    @login_required
    def socials(self):
        return render_template("socials.html")

    @login_required
    def log_completion(self, dest_id):
        init_db(current_app)
        user_id = session["user_id"]
        destination = next(
            (d for d in self._sample_destinations() if d["id"] == dest_id),
            self._sample_destination(dest_id),
        )
        if BaseModel.has_logged_trek(user_id, destination["name"]):
            flash("You have already logged this trek as completed.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))
        BaseModel.log_trek_completion(
            user_id,
            destination["name"],
            destination["difficulty"],
            destination["duration_days"],
        )
        new_badges = BaseModel.check_and_award_new_badges(user_id)
        for badge in new_badges:
            BaseModel.add_notification(
                user_id,
                f"You earned the \"{badge['name']}\" badge {badge['icon']}! {badge['desc']}."
            )
        if new_badges:
            names = ", ".join(b["name"] for b in new_badges)
            flash(f"Trek logged! New badge(s) unlocked: {names} — check your Badges page!", "success")
        else:
            flash("Trek logged as completed. Keep going for more badges!", "success")
        return redirect(url_for("auth.destination_detail", dest_id=dest_id))

    @login_required
    def badges(self):
        init_db(current_app)
        user_id = session["user_id"]
        earned_rows = BaseModel.get_user_badges(user_id)
        earned_map = {row["badge_slug"]: row["earned_at"] for row in earned_rows}
        stats = BaseModel.get_completed_trek_stats(user_id)
        badge_list = []
        for badge in BaseModel.BADGE_DEFINITIONS:
            slug = badge["slug"]
            current, target = BaseModel.badge_progress(slug, stats)
            badge_list.append({
                **badge,
                "is_earned": slug in earned_map,
                "earned_at": earned_map.get(slug),
                "progress_current": current,
                "progress_target": target,
                "progress_pct": int(current / target * 100) if target else 0,
            })
        earned_count = sum(1 for b in badge_list if b["is_earned"])
        return render_template(
            "badges.html",
            badge_list=badge_list,
            earned_count=earned_count,
            total_badges=len(badge_list),
            stats=stats,
        )

    @login_required
    def notifications_read(self):
        init_db(current_app)
        BaseModel.mark_all_notifications_read(session["user_id"])
        return redirect(request.referrer or url_for("auth.home"))

    @login_required
    def checklist(self):
        init_db(current_app)
        user_id = session["user_id"]
        items = BaseModel.get_checklist(user_id)
        categories = {}
        for item in items:
            categories.setdefault(item["category"], []).append(item)
        total = len(items)
        packed = sum(1 for i in items if i["is_checked"])
        return render_template("checklist.html", categories=categories, total=total, packed=packed)

    @login_required
    def checklist_add(self):
        init_db(current_app)
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "General").strip()
        if name:
            BaseModel.add_checklist_item(session["user_id"], name, category)
            flash(f'"{name}" added to your checklist.', "success")
        else:
            flash("Item name cannot be empty.", "error")
        return redirect(url_for("auth.checklist"))

    @login_required
    def checklist_toggle(self, item_id):
        init_db(current_app)
        BaseModel.toggle_checklist_item(session["user_id"], item_id)
        return redirect(url_for("auth.checklist"))

    @login_required
    def checklist_edit(self, item_id):
        init_db(current_app)
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "General").strip()
        if name:
            BaseModel.update_checklist_item(session["user_id"], item_id, name, category)
            flash("Item updated.", "success")
        else:
            flash("Item name cannot be empty.", "error")
        return redirect(url_for("auth.checklist"))

    @login_required
    def checklist_delete(self, item_id):
        init_db(current_app)
        BaseModel.delete_checklist_item(session["user_id"], item_id)
        flash("Item removed.", "success")
        return redirect(url_for("auth.checklist"))

    @login_required
    def checklist_reset(self):
        init_db(current_app)
        BaseModel.reset_checklist(session["user_id"])
        flash("Checklist reset to defaults.", "success")
        return redirect(url_for("auth.checklist"))

    @login_required
    def submit_review(self, dest_id):
        init_db(current_app)
        user_id = session["user_id"]
        destination = next(
            (d for d in self._sample_destinations() if d["id"] == dest_id),
            self._sample_destination(dest_id),
        )
        if not BaseModel.can_review_destination(user_id, destination["name"]):
            flash("You can only review treks you have completed.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))
        if BaseModel.get_user_review_for_dest(user_id, dest_id):
            flash("You have already reviewed this trek.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))
        try:
            rating = int(request.form.get("rating", 0))
        except ValueError:
            rating = 0
        comment = request.form.get("comment", "").strip()
        if rating < 1 or rating > 5:
            flash("Please select a star rating.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))
        if len(comment) < 10:
            flash("Your review must be at least 10 characters.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))
        if len(comment) > 2000:
            flash("Your review cannot exceed 2000 characters.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))
        try:
            BaseModel.add_destination_review(user_id, dest_id, rating, comment)
        except Exception:
            flash("Could not save your review right now.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))
        flash("Your review has been posted!", "success")
        return redirect(url_for("auth.destination_detail", dest_id=dest_id))

    @login_required
    def edit_review(self, dest_id, review_id):
        init_db(current_app)
        user_id = session["user_id"]
        existing = BaseModel.get_user_review_for_dest(user_id, dest_id)
        if not existing or existing["id"] != review_id:
            flash("Review not found.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))
        elapsed = (datetime.utcnow() - existing["created_at"]).total_seconds()
        if elapsed > 600:
            flash("The 10-minute edit window has passed.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))
        try:
            rating = int(request.form.get("rating", 0))
        except ValueError:
            rating = 0
        comment = request.form.get("comment", "").strip()
        if rating < 1 or rating > 5:
            flash("Please select a star rating.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))
        if len(comment) < 10:
            flash("Your review must be at least 10 characters.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))
        if len(comment) > 2000:
            flash("Your review cannot exceed 2000 characters.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))
        try:
            BaseModel.update_destination_review(user_id, review_id, rating, comment)
        except Exception:
            flash("Could not update your review right now.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))
        flash("Your review has been updated!", "success")
        return redirect(url_for("auth.destination_detail", dest_id=dest_id))

    @login_required
    def toggle_favorite(self, dest_id):
        user_id = session["user_id"]
        try:
            favorite_ids = BaseModel.get_favorite_destination_ids(user_id)
        except Exception:
            favorite_ids = []
        try:
            init_db(current_app)
            if dest_id in favorite_ids:
                BaseModel.remove_favorite_destination(user_id, dest_id)
                flash("Destination removed from your favorites.", "success")
            else:
                BaseModel.add_favorite_destination(user_id, dest_id)
                flash("Destination added to your favorites.", "success")
        except Exception:
            flash("Could not update favorites right now.", "error")
        return redirect(url_for("auth.destination_detail", dest_id=dest_id))

    @login_required
    def favorites(self):
        try:
            favorites = BaseModel.get_user_favorites(session["user_id"])
        except Exception:
            flash("Could not load your favorites right now.", "error")
            favorites = []
        return render_template("favorites.html", favorites=favorites)
