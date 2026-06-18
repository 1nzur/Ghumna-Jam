import os
import secrets
import re
from datetime import datetime, timedelta
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

    @staticmethod
    def _is_valid_email(email):
        return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

    @staticmethod
    def _is_strong_password(password):
        return (
            len(password) >= 8
            and re.search(r"[A-Z]", password)
            and re.search(r"\d", password)
            and re.search(r"[!@#$%^&*(),.?\":{}|<>~`_\-\\\[\];'\/+=]", password)
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
            "altitude_meters": 5364,
            "highlights": "Sherpa culture, Kala Patthar viewpoint, historic base camp",
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
                "altitude_meters": 5416,
                "highlights": "Thorong La Pass, Kali Gandaki Gorge, diverse landscapes",
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
                "altitude_meters": 3870,
                "highlights": "Kyanjin Gompa, Yak pastures, panoramic glaciers",
            },
            {
                "id": 4,
                "name": "Manaslu Circuit",
                "image_url": "https://images.unsplash.com/photo-1605649487212-47bdab064df7?auto=format&fit=crop&w=1200&q=80",
                "difficulty": "Challenging",
                "duration_days": 14,
                "season": "Oct-Nov",
                "description": "A remote, spectacular loop around the world's eighth-highest mountain, featuring the challenging Larkya La Pass.",
                "price_per_person": 1399.00 * self.EXCHANGE_RATE,
                "altitude_meters": 5106,
                "highlights": "Larkya La Pass, Buddhist monasteries, border region cultures",
            },
            {
                "id": 5,
                "name": "Upper Mustang",
                "image_url": "https://images.unsplash.com/photo-1548565431-7e8c312521f7?auto=format&fit=crop&w=1200&q=80",
                "difficulty": "Moderate",
                "duration_days": 10,
                "season": "May-Oct",
                "description": "Explore the ancient, dry kingdom of Lo Manthang, characterized by red cliffs, cave dwellings, and Tibetan culture.",
                "price_per_person": 1799.00 * self.EXCHANGE_RATE,
                "altitude_meters": 3840,
                "highlights": "Lo Manthang walled city, sky caves, Tibetan-style palace",
            },
            {
                "id": 6,
                "name": "Gokyo Lakes & Ri",
                "image_url": "https://images.unsplash.com/photo-1589308078059-be1415eab4c3?auto=format&fit=crop&w=1200&q=80",
                "difficulty": "Moderate",
                "duration_days": 12,
                "season": "Mar-May, Sep-Nov",
                "description": "Trek to the turquoise glacial lakes of the Gokyo Valley and climb Gokyo Ri for premium views of Everest and Lhotse.",
                "price_per_person": 1299.00 * self.EXCHANGE_RATE,
                "altitude_meters": 5357,
                "highlights": "Turquoise lakes, Ngozumpa Glacier, views of four 8,000m peaks",
            },
            {
                "id": 7,
                "name": "Kanchenjunga Base Camp",
                "image_url": "https://images.unsplash.com/photo-1533240332313-0db49b459ad6?auto=format&fit=crop&w=1200&q=80",
                "difficulty": "Challenging",
                "duration_days": 20,
                "season": "Oct-Nov, Mar-May",
                "description": "A long journey to the far eastern border of Nepal to reach the base camp of Kanchenjunga, the world's third highest peak.",
                "price_per_person": 2199.00 * self.EXCHANGE_RATE,
                "altitude_meters": 5143,
                "highlights": "Remote wilderness, Limbu culture, views of Yalung glacier",
            },
            {
                "id": 8,
                "name": "Mardi Himal",
                "image_url": "https://images.unsplash.com/photo-1491555180598-88ee14744f4f?auto=format&fit=crop&w=1200&q=80",
                "difficulty": "Easy",
                "duration_days": 6,
                "season": "Mar-May, Sep-Nov",
                "description": "A short, beautiful trek offering up-close views of Mount Machapuchare (Fishtail) and the Annapurna range.",
                "price_per_person": 599.00 * self.EXCHANGE_RATE,
                "altitude_meters": 4500,
                "highlights": "Machapuchare views, forest trails, quiet teahouses",
            },
            {
                "id": 9,
                "name": "Poon Hill Trek",
                "image_url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
                "difficulty": "Easy",
                "duration_days": 5,
                "season": "Sep-May",
                "description": "A classic short trek in the Annapurna foothills, famous for its panoramic sunrise views over Dhaulagiri and Annapurna.",
                "price_per_person": 499.00 * self.EXCHANGE_RATE,
                "altitude_meters": 3210,
                "highlights": "Sunrise over Annapurna, rhododendron forests, Gurung heritage",
            },
            {
                "id": 10,
                "name": "Gosaikunda Lake",
                "image_url": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1200&q=80",
                "difficulty": "Moderate",
                "duration_days": 7,
                "season": "May-Oct",
                "description": "A holy alpine lake trek in the Langtang region, sacred to both Hindus and Buddhists.",
                "price_per_person": 699.00 * self.EXCHANGE_RATE,
                "altitude_meters": 4380,
                "highlights": "Sacred alpine lakes, Laurebina Pass, views of Ganesh Himal",
            },
            {
                "id": 11,
                "name": "Rara Lake Wilderness",
                "image_url": "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&w=1200&q=80",
                "difficulty": "Moderate",
                "duration_days": 9,
                "season": "Mar-May, Sep-Nov",
                "description": "Trek through the untouched forests of western Nepal to the largest and deepest freshwater lake in the country.",
                "price_per_person": 1099.00 * self.EXCHANGE_RATE,
                "altitude_meters": 2990,
                "highlights": "Pristine pine forests, bird watching, boating on Rara Lake",
            },
            {
                "id": 12,
                "name": "Makalu Base Camp",
                "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80",
                "difficulty": "Challenging",
                "duration_days": 18,
                "season": "Sep-Nov, Mar-May",
                "description": "A challenging journey through the Makalu Barun National Park to the base of the world's fifth-highest peak.",
                "price_per_person": 1899.00 * self.EXCHANGE_RATE,
                "altitude_meters": 4870,
                "highlights": "Barun river valley, hanging glaciers, granite cliffs",
            },
            {
                "id": 13,
                "name": "Upper Dolpo Wilderness",
                "image_url": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1200&q=80",
                "difficulty": "Challenging",
                "duration_days": 21,
                "season": "Jun-Sep",
                "description": "A high-altitude, trans-Himalayan trek in the isolated Shey Phoksundo National Park, featuring Bon Buddhist heritage.",
                "price_per_person": 2499.00 * self.EXCHANGE_RATE,
                "altitude_meters": 5130,
                "highlights": "Phoksundo Lake, Shey Gompa, snow leopard habitats",
            },
            {
                "id": 14,
                "name": "Nar Phu Valley hidden villages",
                "image_url": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
                "difficulty": "Challenging",
                "duration_days": 11,
                "season": "Sep-Nov, Mar-May",
                "description": "Explore the hidden Tibetan valleys of Nar and Phu, with ancient stone villages and high pass crossings.",
                "price_per_person": 1499.00 * self.EXCHANGE_RATE,
                "altitude_meters": 5320,
                "highlights": "Kang La Pass, ancient fortified villages, unique monasteries",
            },
            {
                "id": 15,
                "name": "Everest Three Passes",
                "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
                "difficulty": "Challenging",
                "duration_days": 19,
                "season": "Mar-May, Sep-Nov",
                "description": "The ultimate Khumbu adventure crossing three high passes: Renjo La, Cho La, and Kongma La.",
                "price_per_person": 1999.00 * self.EXCHANGE_RATE,
                "altitude_meters": 5535,
                "highlights": "Kongma La, Cho La, Renjo La, Gokyo lakes, Everest Base Camp",
            },
        ]

    @staticmethod
    def _ensure_upload_directory():
        upload_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "static", "uploads")
        )
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

    @staticmethod
    def _save_profile_picture(file_storage, user_id):
        if not file_storage or file_storage.filename == "":
            return None

        upload_dir = AuthController._ensure_upload_directory()
        filename = secure_filename(file_storage.filename)
        filename = f"user_{user_id}_{secrets.token_hex(8)}_{filename}"
        filepath = os.path.join(upload_dir, filename)
        file_storage.save(filepath)
        return url_for("static", filename=f"uploads/{filename}")

    @staticmethod
    def _generate_password_reset_token(email):
        return BaseModel.generate_password_reset_token(email)

    @staticmethod
    def _is_token_valid(token):
        user = BaseModel.get_user_by_reset_token(token)
        return user

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

            if not self._is_valid_email(email):
                flash("Please enter a valid email address with a domain (for example user@example.com).", "error")
                return render_template("signup.html"), 400

            if not self._is_strong_password(password):
                flash(
                    "Password must be at least 8 characters and include 1 uppercase letter, 1 number, and 1 special character.",
                    "error",
                )
                return render_template("signup.html"), 400

            try:
                init_db(current_app)
                BaseModel.create_user(full_name, email, password)
            except ValueError as exc:
                message = str(exc).strip().lower()
                if "already exists" in message or "already used" in message:
                    flash("Account already registered, please log in.", "error")
                    return redirect(url_for("auth.login"))
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
        try:
            destinations = BaseModel.get_all_destinations()
        except Exception:
            flash("Could not load destinations right now.", "error")
            destinations = []

        favorite_ids = []
        if "user_id" in session:
            try:
                favorite_ids = BaseModel.get_favorite_destination_ids(session["user_id"])
            except Exception:
                favorite_ids = []

        return render_template(
            "landpage.html",
            destinations=destinations,
            favorite_ids=favorite_ids,
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

            try:
                init_db(current_app)
                token = self._generate_password_reset_token(email)
            except Exception:
                flash("We could not process that request right now.", "error")
                return render_template("forgot_password.html", email=email), 500

            submitted_email = email
            reset_link = None
            if token:
                reset_link = url_for("auth.reset_password", token=token, _external=False)
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

        try:
            destinations = BaseModel.get_all_destinations()
        except Exception:
            flash("Could not load destinations right now.", "error")
            destinations = []

        selected_treks = BaseModel.get_destinations_by_ids(selected_ids) if selected_ids else []

        return render_template(
            "compare.html",
            destinations=destinations,
            selected_treks=selected_treks,
            selected_ids=selected_ids,
        )

    @login_required
    def bookings(self):
        try:
            bookings = BaseModel.get_user_bookings(session["user_id"])
        except Exception:
            flash("Could not load booking history at the moment.", "error")
            bookings = []
        return render_template("bookings.html", bookings=bookings)

    def destination_detail(self, dest_id):
        destination = BaseModel.get_destination_by_id(dest_id)
        if not destination:
            flash("Destination not found.", "error")
            return redirect(url_for("auth.home"))

        destination_reviews = BaseModel.get_reviews_for_destination(dest_id)
        average_rating_info = BaseModel.get_average_rating_for_destination(dest_id)
        average_rating = average_rating_info.get("average_rating") or 0
        review_count = average_rating_info.get("review_count") or 0
        favorite_ids = []

        if "user_id" in session:
            favorite_ids = BaseModel.get_favorite_destination_ids(session["user_id"])

        return render_template(
            "destination_detail.html",
            destination=destination,
            hotel_options=self._hotel_options(dest_id),
            reviews=destination_reviews,
            average_rating=average_rating,
            review_count=review_count,
            favorite_ids=favorite_ids,
        )

    @login_required
    def book_trip(self, dest_id):
        destination = BaseModel.get_destination_by_id(dest_id)
        if not destination:
            flash("Destination not found.", "error")
            return redirect(url_for("auth.compare_treks"))

        travelers_count = int(request.form.get("travelers_count", 1) or 1)
        departure_date = request.form.get("departure_date", None)
        selected_hotel = request.form.get("selected_hotel", "No hotel selected")

        if travelers_count < 1:
            flash("Please select at least one traveler.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))

        try:
            init_db(current_app)
            BaseModel.create_booking(
                session["user_id"],
                destination["id"],
                destination["name"],
                destination["image_url"],
                departure_date,
                travelers_count,
                destination["duration_days"],
                destination["difficulty"],
                selected_hotel,
                "Confirmed",
                destination["price_per_person"] * travelers_count,
            )
        except Exception:
            flash("We could not complete your booking right now.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))

        flash("Your journey has been added to your bookings.", "success")
        return redirect(url_for("auth.bookings"))

    @login_required
    def cancel_booking(self, booking_id):
        try:
            init_db(current_app)
            BaseModel.cancel_booking(session["user_id"], booking_id)
            flash("Booking cancelled successfully.", "success")
        except Exception:
            flash("Could not cancel the booking right now.", "error")

        return redirect(url_for("auth.bookings"))

    @login_required
    def submit_review(self, dest_id):
        rating = request.form.get("rating", "0")
        comment = request.form.get("comment", "").strip()

        try:
            rating_value = int(rating)
        except ValueError:
            rating_value = 0

        if rating_value < 1 or rating_value > 5:
            flash("Please provide a rating between 1 and 5.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))

        try:
            init_db(current_app)
            BaseModel.add_destination_review(session["user_id"], dest_id, rating_value, comment)
        except Exception:
            flash("We could not save your review right now.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))

        flash("Thank you for your review!", "success")
        return redirect(url_for("auth.destination_detail", dest_id=dest_id))

    @login_required
    def toggle_favorite(self, dest_id):
        user_id = session["user_id"]
        favorite_ids = []
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

    @login_required
    def edit_profile(self):
        user = BaseModel.get_user_by_id(session["user_id"])
        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            phone_number = request.form.get("phone_number", "").strip()
            date_of_birth = request.form.get("date_of_birth", "").strip() or None
            emergency_contact_name = request.form.get("emergency_contact_name", "").strip() or None
            emergency_contact_phone = request.form.get("emergency_contact_phone", "").strip() or None
            password = request.form.get("password", "")
            profile_picture = request.files.get("profile_picture")
            profile_picture_url = None

            if not full_name or not email:
                flash("Name and email are required.", "error")
                return render_template("edit-profile.html", user=user), 400

            if not self._is_valid_email(email):
                flash("Please enter a valid email address with a domain (for example user@example.com).", "error")
                return render_template("edit-profile.html", user=user), 400

            if password and not self._is_strong_password(password):
                flash(
                    "Password must be at least 8 characters and include 1 uppercase letter, 1 number, and 1 special character.",
                    "error",
                )
                return render_template("edit-profile.html", user=user), 400

            if profile_picture and profile_picture.filename:
                try:
                    profile_picture_url = self._save_profile_picture(profile_picture, session["user_id"])
                except Exception:
                    flash("Could not upload profile picture. Please try again.", "error")
                    return render_template("edit-profile.html", user=user), 500
            else:
                profile_picture_url = user.get("profile_picture_url")

            try:
                init_db(current_app)
                BaseModel.update_user(
                    session["user_id"],
                    full_name,
                    email,
                    phone_number=phone_number or None,
                    date_of_birth=date_of_birth,
                    profile_picture_url=profile_picture_url,
                    emergency_contact_name=emergency_contact_name,
                    emergency_contact_phone=emergency_contact_phone,
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

    @login_required
    def tracking(self):
        trail_logs = []
        if request.method == "POST":
            title = request.form.get("title", "Untitled Trail")
            description = request.form.get("description", "")
            log_data = request.form.get("log_data", "")

            try:
                init_db(current_app)
                BaseModel.save_trail_log(session["user_id"], title, description, log_data)
                flash("Trail log saved successfully.", "success")
            except Exception:
                flash("Could not save your trail log right now.", "error")

        try:
            trail_logs = BaseModel.get_user_trails(session["user_id"])
        except Exception:
            trail_logs = []

        return render_template("tracking.html", trail_logs=trail_logs)
