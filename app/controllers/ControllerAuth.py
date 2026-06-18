from functools import wraps
import random
from datetime import datetime, timedelta

from flask import current_app, flash, redirect, render_template, request, session, url_for
from flask_mail import Mail, Message

from app.models.base_model import BaseModel
from app.models.database import init_db

mail = Mail()


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
            4: [
                {"name": "Manaslu Mountain Resort", "location": "Samagaon", "style": "Resort", "price_per_night": 6000, "perk": "Close to Manaslu Base Camp"},
                {"name": "Larkya Rest House", "location": "Dharmasala", "style": "Tea house", "price_per_night": 4500, "perk": "Last stop before the pass"},
            ],
            5: [
                {"name": "Mustang Heritage Hotel", "location": "Lo Manthang", "style": "Heritage", "price_per_night": 7500, "perk": "Traditional Tibetan architecture"},
                {"name": "Oasis Guesthouse", "location": "Charang", "style": "Guesthouse", "price_per_night": 5500, "perk": "Views of the ancient monastery"},
            ],
            6: [
                {"name": "Gokyo Lake Resort", "location": "Gokyo", "style": "Lakeside Lodge", "price_per_night": 8000, "perk": "Direct views of Gokyo Lake"},
                {"name": "Ngozumpa Inn", "location": "Machhermo", "style": "Inn", "price_per_night": 6500, "perk": "Cozy dining room"},
            ],
            7: [
                {"name": "Kanchenjunga Base Camp Lodge", "location": "Pangpema", "style": "Base Camp Lodge", "price_per_night": 6000, "perk": "Closest to the mountain"},
                {"name": "Yalung Glacier Retreat", "location": "Ramche", "style": "Retreat", "price_per_night": 5000, "perk": "Glacier views"},
            ],
            8: [
                {"name": "Mardi High Camp Lodge", "location": "High Camp", "style": "Lodge", "price_per_night": 5500, "perk": "Sunset views of Machapuchare"},
                {"name": "Forest Camp Rest", "location": "Forest Camp", "style": "Eco-lodge", "price_per_night": 4000, "perk": "Immersive forest experience"},
            ],
            9: [
                {"name": "Poon Hill Sunrise Hotel", "location": "Ghorepani", "style": "Hotel", "price_per_night": 5000, "perk": "Quick access to Poon Hill"},
                {"name": "Ulleri Steps Inn", "location": "Ulleri", "style": "Inn", "price_per_night": 3500, "perk": "Rest after the steep climb"},
            ],
            10: [
                {"name": "Sacred Lake Lodge", "location": "Gosaikunda", "style": "Lakeside Lodge", "price_per_night": 6500, "perk": "Right by the holy lake"},
                {"name": "Laurebina Pass Retreat", "location": "Laurebina", "style": "Retreat", "price_per_night": 5500, "perk": "Panoramic mountain views"},
            ],
            11: [
                {"name": "Rara Lake View Resort", "location": "Rara", "style": "Resort", "price_per_night": 8000, "perk": "Boating and lake views"},
                {"name": "Pine Forest Guesthouse", "location": "Talcha", "style": "Guesthouse", "price_per_night": 4500, "perk": "Quiet forest setting"},
            ],
            12: [
                {"name": "Makalu Base Camp Hut", "location": "Makalu Base Camp", "style": "Hut", "price_per_night": 7000, "perk": "Base camp experience"},
                {"name": "Barun Valley Inn", "location": "Yangle Kharka", "style": "Inn", "price_per_night": 5000, "perk": "Beautiful valley views"},
            ],
            13: [
                {"name": "Phoksundo Lake Hotel", "location": "Ringmo", "style": "Hotel", "price_per_night": 8500, "perk": "Overlooking the turquoise lake"},
                {"name": "Shey Gompa Rest", "location": "Shey Gompa", "style": "Rest house", "price_per_night": 6000, "perk": "Near the ancient monastery"},
            ],
            14: [
                {"name": "Nar Village Homestay", "location": "Nar", "style": "Homestay", "price_per_night": 4500, "perk": "Authentic local culture"},
                {"name": "Phu Heritage Lodge", "location": "Phu", "style": "Lodge", "price_per_night": 5000, "perk": "Historic stone village setting"},
            ],
            15: [
                {"name": "Kongma La Rest", "location": "Chukhung", "style": "Lodge", "price_per_night": 6000, "perk": "Preparation for the first pass"},
                {"name": "Renjo La Viewpoint Hotel", "location": "Lungden", "style": "Hotel", "price_per_night": 6500, "perk": "Stunning sunset views"},
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
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            if not email:
                flash("Please enter your email address.", "error")
                return render_template("forgot_password.html"), 400
            
            init_db(current_app)
            user = BaseModel.get_user_by_email(email)
            if user:
                # Generate 6-digit OTP
                otp_code = f"{random.randint(100000, 999999)}"
                expiry_time = datetime.now() + timedelta(minutes=current_app.config.get("OTP_EXPIRY_MINUTES", 10))
                
                BaseModel.save_otp(email, otp_code, expiry_time)
                
                # Send Email or print to console
                try:
                    msg = Message(
                        "Your Password Reset OTP",
                        recipients=[email]
                    )
                    msg.body = f"Your OTP for password reset is: {otp_code}\n\nIt will expire in 10 minutes."
                    mail.send(msg)
                    print(f"OTP sent to {email}: {otp_code}") # Fallback print for development
                except Exception as e:
                    print(f"Failed to send email. OTP for {email} is {otp_code}. Error: {e}")
            
            session["reset_email"] = email
            flash("If that email exists, reset instructions will be sent.", "success")
            return redirect(url_for("auth.verify_otp"))
            
        return render_template("forgot_password.html")

    def verify_otp(self):
        email = session.get("reset_email")
        if not email:
            flash("Session expired. Please request a new password reset.", "error")
            return redirect(url_for("auth.forgot_password"))

        if request.method == "POST":
            otp_code = request.form.get("otp_code", "").strip()
            
            if not otp_code:
                flash("Please enter the OTP.", "error")
                return render_template("verify_otp.html", email=email), 400
                
            user = BaseModel.get_valid_otp_user(email, otp_code)
            
            if user:
                session["otp_verified"] = True
                flash("OTP verified successfully. Please enter your new password.", "success")
                return redirect(url_for("auth.reset_password"))
            else:
                flash("Invalid or expired OTP.", "error")
                return render_template("verify_otp.html", email=email), 400

        return render_template("verify_otp.html", email=email)

    def reset_password(self):
        email = session.get("reset_email")
        if not email or not session.get("otp_verified"):
            flash("Unauthorized access. Please verify your OTP first.", "error")
            return redirect(url_for("auth.forgot_password"))

        if request.method == "POST":
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")
            
            if not password or not confirm_password:
                flash("Please fill in all fields.", "error")
                return render_template("reset_password.html"), 400
                
            if password != confirm_password:
                flash("Passwords do not match.", "error")
                return render_template("reset_password.html"), 400
                
            try:
                BaseModel.update_password_by_email(email, password)
                # Clear session variables
                session.pop("reset_email", None)
                session.pop("otp_verified", None)
                flash("Your password has been reset successfully. You can now log in.", "success")
                return redirect(url_for("auth.login"))
            except Exception as e:
                flash("We could not reset your password right now.", "error")
                print(f"Error resetting password: {e}")
                return render_template("reset_password.html"), 500
                
        return render_template("reset_password.html")
    
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
        return render_template("bookings.html", bookings=session.get("bookings", []))

    def destination_detail(self, dest_id):
        destination = next(
            (dest for dest in self._sample_destinations() if dest["id"] == dest_id),
            self._sample_destination(dest_id),
        )
        return render_template(
            "destination_detail.html",
            destination=destination,
            hotel_options=self._hotel_options(dest_id),
        )

    @login_required
    def book_trip(self, dest_id):
        destination = next(
            (dest for dest in self._sample_destinations() if dest["id"] == dest_id),
            self._sample_destination(dest_id),
        )
        travelers_count = int(request.form.get("travelers_count", 1) or 1)
        departure_date = request.form.get("departure_date", "Not selected")
        selected_hotel = request.form.get("selected_hotel", "No hotel selected")
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
                "selected_hotel": selected_hotel,
                "booked_at": "Today",
                "total_price": destination["price_per_person"] * travelers_count,
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
            profile_picture_url = request.form.get("profile_picture_url", "").strip()
            password = request.form.get("password", "")

            if not full_name or not email:
                flash("Name and email are required.", "error")
                return render_template("edit-profile.html", user=user), 400

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

    @login_required
    def tracking(self):
        return render_template("tracking.html")

    @login_required
    def packing_checklist(self):
        return render_template("packing_checklist.html")

    @login_required
    def recommendations(self):
        destinations = self._sample_destinations()
        return render_template("recommended_treks.html", destinations=destinations)
