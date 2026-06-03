import os
from functools import wraps

from flask import current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

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
    ALLOWED_PROFILE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    MAX_PROFILE_PICTURE_BYTES = 2 * 1024 * 1024

    def _allowed_profile_picture(self, filename):
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.ALLOWED_PROFILE_EXTENSIONS
        )

    def _sample_destination(self, dest_id=1):
        return {
            "id": dest_id,
            "name": "Everest Base Camp",
            "image_url": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
            "difficulty": "Moderate",
            "duration_days": 14,
            "season": "Mar-May, Sep-Nov",
            "description": "A classic Himalayan trek through Sherpa villages, alpine valleys, and dramatic views of the world's highest peaks.",
            "price_per_person": 1499.00 * self.EXCHANGE_RATE,
        }

    def _sample_destinations(self):
        return [
            self._sample_destination(1),
            {
                "id": 2,
                "name": "Annapurna Circuit",
                "image_url": "https://images.unsplash.com/photo-1517021897933-0e0319cfbc28?auto=format&fit=crop&w=1200&q=80",
                "difficulty": "Challenging",
                "duration_days": 12,
                "season": "Oct-Nov",
                "description": "A sweeping circuit through river valleys, high passes, and traditional mountain settlements.",
                "price_per_person": 1199.00 * self.EXCHANGE_RATE,
            },
            {
                "id": 3,
                "name": "Langtang Valley",
                "image_url": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
                "difficulty": "Moderate",
                "duration_days": 8,
                "season": "Mar-May",
                "description": "A beautiful alpine route with glacier views, yak pastures, and rich Tamang culture.",
                "price_per_person": 799.00 * self.EXCHANGE_RATE,
            },
        ]

    def _hotel_options_for_destination(self, dest_id):
        hotel_sets = {
            1: [
                {
                    "id": "trail-teahouse",
                    "name": "Trailside Tea House",
                    "tier": "Included",
                    "location": "Phakding and Namche",
                    "description": "Classic mountain tea-house rooms selected by the guide team for warm dining rooms and easy trail access.",
                    "amenities": ["Shared bath", "Breakfast", "Guide-picked"],
                    "price_per_person": 0,
                },
                {
                    "id": "namche-comfort",
                    "name": "Namche Comfort Lodge",
                    "tier": "Popular",
                    "location": "Namche Bazaar",
                    "description": "Private twin rooms on key acclimatization nights with hot showers where available and quieter rest stops.",
                    "amenities": ["Private room", "Hot shower", "Wi-Fi zones"],
                    "price_per_person": 4500,
                },
                {
                    "id": "heritage-hotel",
                    "name": "Kathmandu Heritage Hotel + Lodge",
                    "tier": "Premium",
                    "location": "Kathmandu and Khumbu",
                    "description": "A boutique Kathmandu hotel before the trek plus the best available lodge stays along the route.",
                    "amenities": ["Airport pickup", "Boutique stay", "Best rooms"],
                    "price_per_person": 9500,
                },
            ],
            2: [
                {
                    "id": "trail-teahouse",
                    "name": "Annapurna Tea House",
                    "tier": "Included",
                    "location": "Dharapani to Muktinath",
                    "description": "Reliable local lodges near the circuit villages with hearty dining rooms and quick access to the trail.",
                    "amenities": ["Shared bath", "Breakfast", "Village stays"],
                    "price_per_person": 0,
                },
                {
                    "id": "manang-comfort",
                    "name": "Manang View Lodge",
                    "tier": "Popular",
                    "location": "Manang and Lower Mustang",
                    "description": "Comfort-focused rooms during acclimatization stops, chosen for mountain views and calmer evenings.",
                    "amenities": ["Private room", "Hot shower", "View rooms"],
                    "price_per_person": 4200,
                },
                {
                    "id": "pokhara-retreat",
                    "name": "Pokhara Lakeside Retreat + Lodge",
                    "tier": "Premium",
                    "location": "Pokhara and Annapurna",
                    "description": "Adds a lakeside recovery hotel in Pokhara and upgraded rooms where the circuit has availability.",
                    "amenities": ["Lakeside hotel", "Airport pickup", "Best rooms"],
                    "price_per_person": 8900,
                },
            ],
            3: [
                {
                    "id": "trail-teahouse",
                    "name": "Langtang Tea House",
                    "tier": "Included",
                    "location": "Lama Hotel to Kyanjin",
                    "description": "Family-run lodges with warm meals, simple rooms, and direct access to the valley trail.",
                    "amenities": ["Shared bath", "Breakfast", "Family lodges"],
                    "price_per_person": 0,
                },
                {
                    "id": "kyanjin-comfort",
                    "name": "Kyanjin Comfort Lodge",
                    "tier": "Popular",
                    "location": "Kyanjin Gompa",
                    "description": "Upgraded rest nights near the monastery with better bedding and glacier-view common areas.",
                    "amenities": ["Private room", "Hot drinks", "View lounge"],
                    "price_per_person": 3500,
                },
                {
                    "id": "tamang-heritage",
                    "name": "Tamang Heritage Stay + Lodge",
                    "tier": "Premium",
                    "location": "Syabrubesi and Langtang",
                    "description": "Pairs the valley trek with a curated heritage stay and the best available mountain rooms.",
                    "amenities": ["Heritage stay", "Local dinner", "Best rooms"],
                    "price_per_person": 7200,
                },
            ],
        }
        return hotel_sets.get(dest_id, hotel_sets[1])

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
            flash("Logged in successfully.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("auth.home"))

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
        return render_template(
            "landpage.html",
            destinations=self._sample_destinations(),
            user_name=session.get("user_name"),
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

    @login_required
    def bookings(self):
        return render_template("bookings.html", bookings=session.get("bookings", []))

    def destination_detail(self, dest_id):
        destination = next(
            (dest for dest in self._sample_destinations() if dest["id"] == dest_id),
            self._sample_destination(dest_id),
        )
        return render_template(
            "destination_detail.html",
            destination=destination,
            hotel_options=self._hotel_options_for_destination(dest_id),
        )

    @login_required
    def book_trip(self, dest_id):
        destination = next(
            (dest for dest in self._sample_destinations() if dest["id"] == dest_id),
            self._sample_destination(dest_id),
        )
        try:
            travelers_count = int(request.form.get("travelers_count", 1) or 1)
        except ValueError:
            travelers_count = 1
        travelers_count = max(1, min(travelers_count, 12))
        departure_date = request.form.get("departure_date", "Not selected")
        hotel_options = self._hotel_options_for_destination(dest_id)
        hotel_id = request.form.get("hotel_id", hotel_options[0]["id"])
        selected_hotel = next(
            (hotel for hotel in hotel_options if hotel["id"] == hotel_id),
            hotel_options[0],
        )
        price_per_explorer = (
            destination["price_per_person"] + selected_hotel["price_per_person"]
        )
        bookings = session.get("bookings", [])
        bookings.append(
            {
                "dest_name": destination["name"],
                "dest_image": destination["image_url"],
                "status": "Confirmed",
                "departure_date": departure_date,
                "travelers_count": travelers_count,
                "duration_days": destination["duration_days"],
                "difficulty": destination["difficulty"],
                "hotel_name": selected_hotel["name"],
                "hotel_tier": selected_hotel["tier"],
                "hotel_location": selected_hotel["location"],
                "hotel_price_per_person": selected_hotel["price_per_person"],
                "booked_at": "Today",
                "total_price": price_per_explorer * travelers_count,
            }
        )
        session["bookings"] = bookings
        session.modified = True
        flash("Your journey has been added to your bookings.", "success")
        return redirect(url_for("auth.bookings"))

    @login_required
    def edit_profile(self):
        user = BaseModel.get_user_by_id(session["user_id"])
        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            phone_number = request.form.get("phone_number", "").strip()
            date_of_birth = request.form.get("date_of_birth", "").strip() or None
            profile_picture_url = user.get("profile_picture_url") if user else None
            profile_picture = request.files.get("profile_picture")
            password = request.form.get("password", "")

            if not full_name or not email:
                flash("Name and email are required.", "error")
                return render_template("edit-profile.html", user=user), 400

            if profile_picture and profile_picture.filename:
                if not self._allowed_profile_picture(profile_picture.filename):
                    flash("Please upload a JPG, PNG, GIF, or WEBP profile picture.", "error")
                    return render_template("edit-profile.html", user=user), 400

                profile_picture.stream.seek(0, os.SEEK_END)
                profile_picture_size = profile_picture.stream.tell()
                profile_picture.stream.seek(0)
                if profile_picture_size > self.MAX_PROFILE_PICTURE_BYTES:
                    flash("Profile pictures must be 2MB or smaller.", "error")
                    return render_template("edit-profile.html", user=user), 400

                filename = secure_filename(profile_picture.filename)
                extension = filename.rsplit(".", 1)[1].lower()
                stored_filename = f"user-{session['user_id']}.{extension}"
                upload_folder = os.path.join(
                    current_app.root_path,
                    "static",
                    "uploads",
                    "profile_pictures",
                )
                os.makedirs(upload_folder, exist_ok=True)
                profile_picture.save(os.path.join(upload_folder, stored_filename))
                profile_picture_url = url_for(
                    "static",
                    filename=f"uploads/profile_pictures/{stored_filename}",
                )

            try:
                BaseModel.update_user(
                    session["user_id"],
                    full_name,
                    email,
                    phone_number=phone_number or None,
                    date_of_birth=date_of_birth,
                    profile_picture_url=profile_picture_url or None,
                    password=password or None,
                )
            except ValueError as exc:
                flash(str(exc), "error")
                return render_template("edit-profile.html", user=user), 400
            except Exception:
                flash("We could not update your profile right now.", "error")
                return render_template("edit-profile.html", user=user), 500

            session["user_name"] = full_name
            session["profile_picture_url"] = profile_picture_url or None
            flash("Profile updated successfully.", "success")
            return redirect(url_for("auth.edit_profile"))

        return render_template("edit-profile.html", user=user)

    def logout(self):
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for("auth.login"))
