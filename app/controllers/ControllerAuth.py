import os
import secrets
import re
from datetime import datetime, timedelta
from functools import wraps

from flask import current_app, flash, jsonify, redirect, render_template, request, session, url_for
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
    def _save_trek_photo(file_storage, user_id):
        if not file_storage or file_storage.filename == "":
            return None

        upload_dir = AuthController._ensure_upload_directory()
        filename = secure_filename(file_storage.filename)
        filename = f"trek_{user_id}_{secrets.token_hex(8)}_{filename}"
        filepath = os.path.join(upload_dir, filename)
        file_storage.save(filepath)
        return url_for("static", filename=f"uploads/{filename}")

    @staticmethod
    def _calculate_booking_cost(destination, travelers_count, group_type, package_name):
        travelers_count = max(1, min(int(travelers_count), 24))
        duration_days = int(destination["duration_days"] or 1)
        base_trek_fee = float(destination["price_per_person"]) * travelers_count
        hotel_fee = float(destination.get("hotel_price_per_night") or 2500) * duration_days * travelers_count
        transportation_fee = float(destination.get("transportation_fee") or 15000)
        guide_fee = float(destination.get("guide_fee_per_day") or 3500) * duration_days
        permit_fee = float(destination.get("permit_fee") or 5000) * travelers_count
        group_discount = {"solo": 0, "couple": 0.04, "small_group": 0.08, "large_group": 0.12}.get(group_type, 0)
        package_multiplier = {"standard": 1.0, "comfort": 1.18, "premium": 1.35}.get(package_name, 1.0)
        subtotal = (base_trek_fee + hotel_fee + transportation_fee + guide_fee + permit_fee) * package_multiplier
        subtotal *= 1 - group_discount
        taxes = subtotal * 0.13
        return {
            "trek_fee": round(base_trek_fee, 2),
            "hotel_fee": round(hotel_fee, 2),
            "transportation_fee": round(transportation_fee, 2),
            "guide_fee": round(guide_fee, 2),
            "permit_fee": round(permit_fee, 2),
            "taxes": round(taxes, 2),
            "total": round(subtotal + taxes, 2),
        }

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
        replies = BaseModel.get_replies_for_destination(dest_id)
        replies_by_review = {}
        for reply in replies:
            replies_by_review.setdefault(reply["review_id"], []).append(reply)
        photos = BaseModel.get_destination_photos(dest_id)
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
            replies_by_review=replies_by_review,
            photos=photos,
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
        group_type = request.form.get("group_type", "solo")
        package_name = request.form.get("package_name", "standard")

        if travelers_count < 1:
            flash("Please select at least one traveler.", "error")
            return redirect(url_for("auth.destination_detail", dest_id=dest_id))

        cost = self._calculate_booking_cost(destination, travelers_count, group_type, package_name)
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
                cost["total"],
                group_type=group_type,
                package_name=package_name,
                hotel_fee=cost["hotel_fee"],
                transportation_fee=cost["transportation_fee"],
                guide_fee=cost["guide_fee"],
                permit_fee=cost["permit_fee"],
                taxes=cost["taxes"],
            )
            BaseModel.award_achievements(session["user_id"])
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
            distance_km = request.form.get("distance_km", 0)
            duration_seconds = request.form.get("duration_seconds", 0)
            elevation_gain_m = request.form.get("elevation_gain_m", 0)

            try:
                init_db(current_app)
                BaseModel.save_trail_log(session["user_id"], title, description, log_data, distance_km, duration_seconds, elevation_gain_m)
                BaseModel.award_achievements(session["user_id"])
                flash("Trail log saved successfully.", "success")
            except Exception:
                flash("Could not save your trail log right now.", "error")

        try:
            trail_logs = BaseModel.get_user_trails(session["user_id"])
        except Exception:
            trail_logs = []

        return render_template("tracking.html", trail_logs=trail_logs)

    @login_required
    def trip_history(self):
        # Auto-sync existing bookings into trip_history if empty
        try:
            from app.models.database import get_db
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS count FROM trip_history WHERE user_id = %s", (session["user_id"],))
                if cursor.fetchone()["count"] == 0:
                    cursor.execute("SELECT * FROM bookings WHERE user_id = %s", (session["user_id"],))
                    bkgs = cursor.fetchall()
                    for b in bkgs:
                        cursor.execute(
                            """
                            INSERT IGNORE INTO trip_history (user_id, booking_id, destination_id, history_status, start_date, end_date)
                            VALUES (%s, %s, %s, %s, %s, DATE_ADD(%s, INTERVAL %s DAY))
                            """,
                            (session["user_id"], b["id"], b["destination_id"], 
                             "Cancelled" if b["booking_status"] == "Cancelled" else "Upcoming", 
                             b["departure_date"], b["departure_date"], b["duration_days"])
                        )
                    db.commit()
        except Exception as e:
            print("Error syncing bookings to trip history:", e)

        try:
            trips = BaseModel.get_trip_history(session["user_id"])
        except Exception as e:
            print("Error getting trip history:", e)
            flash("Could not load trip history right now.", "error")
            trips = []

        formatted_trips = []
        today = datetime.utcnow().date()
        for t in trips:
            trip = dict(t)
            trip["trip_id"] = t["id"]
            # Set history status
            status = t["history_status"]
            if status != "Cancelled":
                start = t.get("start_date")
                if start:
                    try:
                        start_parsed = datetime.strptime(str(start), "%Y-%m-%d").date() if isinstance(start, str) else start
                        if start_parsed < today:
                            status = "Completed"
                        else:
                            status = "Yet to be"
                    except ValueError:
                        pass
            trip["history_status"] = status
            formatted_trips.append(trip)

        return render_template("trip_history.html", trips=formatted_trips)

    @login_required
    def trip_detail(self, trip_id):
        try:
            trip = BaseModel.get_trip_detail(session["user_id"], trip_id)
        except Exception as e:
            print("Error getting trip detail:", e)
            trip = None

        if not trip:
            flash("Trip not found.", "error")
            return redirect(url_for("auth.trip_history"))

        today = datetime.utcnow().date()
        status = trip["history_status"]
        if status != "Cancelled":
            start = trip.get("start_date")
            if start:
                try:
                    start_parsed = datetime.strptime(str(start), "%Y-%m-%d").date() if isinstance(start, str) else start
                    if start_parsed < today:
                        status = "Completed"
                    else:
                        status = "Yet to be"
                except ValueError:
                    pass
        trip["history_status"] = status
        # Defaults
        trip["guide_name"] = "Licensed Trek Guide"
        
        return render_template("trip_detail.html", trip=trip)

    @login_required
    def packing_checklist(self):
        items = BaseModel.get_checklist_items(session["user_id"])
        return render_template("packing_checklist.html", checklist_items=items)

    @login_required
    def recommendations(self):
        try:
            recommended = BaseModel.generate_trek_recommendations(session["user_id"])
        except Exception as e:
            print("Error generating recommendations:", e)
            flash("Could not load recommendations right now.", "error")
            recommended = []
        return render_template("recommended_treks.html", destinations=recommended)

    @login_required
    def cost_breakdown(self):
        try:
            destinations = BaseModel.get_all_destinations()
        except Exception:
            destinations = []
        return render_template("costbreakdown.html", destinations=destinations)

    def about_us(self):
        try:
            destinations = BaseModel.get_all_destinations()
        except Exception:
            destinations = []
        return render_template("about-us.html", destinations=destinations)

    @login_required
    def badges(self):
        completed_treks, badge_progress, earned_badges = BaseModel.get_achievement_progress(session["user_id"])
        return render_template("badges.html", completed_treks=completed_treks, badge_progress=badge_progress, earned_badges=earned_badges)

    @login_required
    def follow_page(self):
        search_query = request.args.get("q", "").strip()
        users = BaseModel.list_trekkers(session["user_id"], search_query)
        following_ids = BaseModel.get_following_ids(session["user_id"])
        return render_template(
            "follow.html",
            users=users,
            followers=BaseModel.get_followers(session["user_id"]),
            following=BaseModel.get_following(session["user_id"]),
            following_ids=following_ids,
            suggested_users=[user for user in users if user["id"] not in following_ids][:5],
            notifications=[],
            search_query=search_query,
        )

    @login_required
    def toggle_follow(self, user_id):
        if user_id == session["user_id"]:
            flash("You cannot follow yourself.", "error")
        elif request.form.get("action") == "unfollow":
            BaseModel.unfollow_user(session["user_id"], user_id)
            flash("Trekker unfollowed.", "success")
        else:
            BaseModel.follow_user(session["user_id"], user_id)
            flash("Trekker followed.", "success")
        return redirect(request.form.get("next") or url_for("auth.follow_page"))

    @login_required
    def trekker_profile(self, user_id):
        user = BaseModel.get_user_by_id(user_id)
        if not user:
            flash("Trekker not found.", "error")
            return redirect(url_for("auth.follow_page"))
        return render_template(
            "trekker_profile.html",
            user=user,
            followers=BaseModel.get_followers(user_id),
            following=BaseModel.get_following(user_id),
            trails=BaseModel.get_user_trails(user_id),
            is_following=user_id in BaseModel.get_following_ids(session["user_id"]),
        )

    @login_required
    def post_activity(self):
        flash("Your activity update was shared with your followers.", "success")
        return redirect(url_for("auth.follow_page"))

    @login_required
    def my_reviews(self):
        reviews = BaseModel.get_user_reviews(session["user_id"])
        published = [review for review in reviews if review["status"] == "Published"]
        stats = {
            "total": len(reviews),
            "published": len(published),
            "hidden": len(reviews) - len(published),
            "average_rating": sum(review["rating"] for review in published) / len(published) if published else 0,
        }
        photos = BaseModel.get_user_photos(session["user_id"])
        return render_template("reviews.html", reviews=reviews, stats=stats, photos=photos)

    @login_required
    def edit_review(self, review_id):
        rating = max(1, min(int(request.form.get("rating", "1")), 5))
        comment = request.form.get("comment", "").strip()
        status = request.form.get("status", "Published")
        BaseModel.update_user_review(session["user_id"], review_id, rating, comment, status)
        flash("Review updated.", "success")
        return redirect(url_for("auth.my_reviews"))

    @login_required
    def delete_review(self, review_id):
        BaseModel.delete_user_review(session["user_id"], review_id)
        flash("Review deleted.", "success")
        return redirect(url_for("auth.my_reviews"))

    @login_required
    def reply_to_review(self, review_id):
        body = request.form.get("body", "").strip()
        dest_id = request.form.get("dest_id", type=int)
        if body:
            BaseModel.add_review_reply(review_id, session["user_id"], body)
            flash("Reply added.", "success")
        return redirect(url_for("auth.destination_detail", dest_id=dest_id) + "#reviews")

    @login_required
    def upload_trek_photo(self, dest_id):
        file_path = self._save_trek_photo(request.files.get("photo"), session["user_id"])
        if not file_path:
            flash("Please choose a photo to upload.", "error")
        else:
            BaseModel.upload_trek_photo(session["user_id"], dest_id, file_path, request.form.get("caption", "").strip())
            flash("Photo uploaded to the trek gallery.", "success")
        return redirect(url_for("auth.destination_detail", dest_id=dest_id) + "#gallery")

    @login_required
    def delete_photo(self, photo_id):
        BaseModel.delete_user_photo(session["user_id"], photo_id)
        flash("Photo removed.", "success")
        return redirect(url_for("auth.my_reviews"))

    @login_required
    def add_checklist_item(self):
        item_name = request.form.get("item_name", "").strip()
        if item_name:
            BaseModel.add_checklist_item(session["user_id"], item_name, request.form.get("category", "Gear"))
        return redirect(url_for("auth.packing_checklist"))

    @login_required
    def toggle_checklist_item(self, item_id):
        BaseModel.update_checklist_item(session["user_id"], item_id, bool(request.form.get("is_packed")))
        return redirect(url_for("auth.packing_checklist"))

    @login_required
    def delete_checklist_item(self, item_id):
        BaseModel.delete_checklist_item(session["user_id"], item_id)
        return redirect(url_for("auth.packing_checklist"))

    @login_required
    def create_sos_alert(self):
        data = request.get_json(silent=True) or request.form
        BaseModel.save_emergency_alert(
            session["user_id"],
            data.get("latitude"),
            data.get("longitude"),
            data.get("accuracy_m") or data.get("accuracy"),
            data.get("message", "Emergency SOS triggered from trek tracker."),
        )
        return jsonify({"status": "saved"})

    @login_required
    def complete_trek(self):
        data = request.get_json(silent=True) or {}
        BaseModel.save_trail_log(
            session["user_id"],
            "Completed GPS Trek",
            "Completed from live tracker",
            str(data.get("points", [])),
            data.get("distance_km", 0),
            data.get("duration_seconds", 0),
            data.get("elevation_gain_m", 0),
        )
        BaseModel.award_achievements(session["user_id"])
        return jsonify({"status": "saved"})

    @login_required
    def api_cost_plans(self):
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            plan_name = data.get("plan_name", "My Trek Budget Plan")
            destination_id = int(data.get("destination_id"))
            hotel_tier = data.get("hotel_tier", "standard")
            guide_tier = data.get("guide_tier", "licensed")
            transport_option = data.get("transport_option", "tourist_bus")
            group_size = int(data.get("group_size", 1))
            duration_days = int(data.get("duration_days", 7))
            
            try:
                plan_id = BaseModel.save_cost_plan(
                    session["user_id"], plan_name, destination_id,
                    hotel_tier, guide_tier, transport_option, group_size, duration_days
                )
                return jsonify({"status": "saved", "plan_id": plan_id})
            except Exception as e:
                print("Error saving cost plan:", e)
                return jsonify({"status": "error", "message": str(e)}), 400
        else:
            try:
                plans = BaseModel.get_user_plans(session["user_id"])
                # Convert decimal objects to floats for JSON serialization
                for p in plans:
                    for k, v in p.items():
                        if isinstance(v, (type(None), str, int, float, bool)):
                            continue
                        try:
                            p[k] = float(v)
                        except Exception:
                            p[k] = str(v)
                return jsonify(plans)
            except Exception as e:
                print("Error getting cost plans:", e)
                return jsonify({"status": "error", "message": str(e)}), 500

    @login_required
    def api_delete_cost_plan(self, plan_id):
        try:
            BaseModel.delete_cost_plan(session["user_id"], plan_id)
            return jsonify({"status": "deleted"})
        except Exception as e:
            print("Error deleting cost plan:", e)
            return jsonify({"status": "error", "message": str(e)}), 500
