import os
import re
from datetime import datetime
from functools import wraps

from flask import current_app, flash, redirect, render_template, request, session, url_for

from app.models.base_model import BaseModel
from app.models.database import init_db, get_db


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
            # 1 — Everest Base Camp (Khumbu region)
            1: [
                {
                    "name": "Hotel Everest View",
                    "location": "Namche Bazaar",
                    "style": "Boutique mountain hotel",
                    "price_per_night": 12000,
                    "perk": "Only hotel in the world with a guaranteed Everest view from your room",
                },
                {
                    "name": "Yeti Mountain Home",
                    "location": "Phakding",
                    "style": "Luxury lodge",
                    "price_per_night": 18500,
                    "perk": "Hot showers, en-suite rooms, and solar-heated water",
                },
                {
                    "name": "Pyramid Guest House",
                    "location": "Lobuche",
                    "style": "High-altitude lodge",
                    "price_per_night": 6500,
                    "perk": "Warm yak-dung stoves and hearty dal bhat at 4,940 m",
                },
                {
                    "name": "Gorak Shep Lodge",
                    "location": "Gorak Shep",
                    "style": "Basic mountain lodge",
                    "price_per_night": 5000,
                    "perk": "Last stop before EBC — closest accommodation to base camp",
                },
            ],
            # 2 — Annapurna Circuit
            2: [
                {
                    "name": "Hotel Namaste Manang",
                    "location": "Manang",
                    "style": "Acclimatisation lodge",
                    "price_per_night": 7000,
                    "perk": "Rooftop Annapurna III views; bakery on site",
                },
                {
                    "name": "Thorung High Camp Lodge",
                    "location": "Thorong High Camp",
                    "style": "High camp shelter",
                    "price_per_night": 5500,
                    "perk": "At 4,925 m — last stop before Thorong La Pass",
                },
                {
                    "name": "Hotel Tulsiram",
                    "location": "Chame",
                    "style": "Riverside guesthouse",
                    "price_per_night": 4200,
                    "perk": "Hot spring nearby; apple brandy served in the evening",
                },
                {
                    "name": "Hotel Bob Marley",
                    "location": "Pisang",
                    "style": "Village teahouse",
                    "price_per_night": 3800,
                    "perk": "Stunning Annapurna II views from the rooftop",
                },
            ],
            # 3 — Langtang Valley
            3: [
                {
                    "name": "Kyanjin Gompa Guest House",
                    "location": "Kyanjin Gompa",
                    "style": "Glacier-view lodge",
                    "price_per_night": 5000,
                    "perk": "Walking distance to the famous yak cheese factory",
                },
                {
                    "name": "Langtang Valley Hotel",
                    "location": "Langtang Village",
                    "style": "Rebuilt village lodge",
                    "price_per_night": 4000,
                    "perk": "Community-rebuilt post-2015 earthquake; supports local families",
                },
                {
                    "name": "Lama Hotel & Lodge",
                    "location": "Lama Hotel",
                    "style": "Forest teahouse",
                    "price_per_night": 3200,
                    "perk": "Set in dense rhododendron jungle with red panda sightings",
                },
                {
                    "name": "Hotel Tserko",
                    "location": "Syabrubesi",
                    "style": "Trailhead guesthouse",
                    "price_per_night": 3500,
                    "perk": "Hot water, WiFi, and easy transport connections",
                },
            ],
            # 4 — Manaslu Circuit
            4: [
                {
                    "name": "Birendra Lake Lodge",
                    "location": "Samagaon",
                    "style": "Alpine lodge",
                    "price_per_night": 5500,
                    "perk": "Views of Manaslu and nearby Birendra glacial lake",
                },
                {
                    "name": "Tsum Valley Guesthouse",
                    "location": "Lho",
                    "style": "Village teahouse",
                    "price_per_night": 4000,
                    "perk": "Gateway to sacred Tsum Valley with monastery views",
                },
                {
                    "name": "Dharmasala Lodge",
                    "location": "Samdo",
                    "style": "High-camp lodge",
                    "price_per_night": 4800,
                    "perk": "Highest village before Larkya La Pass at 3,690 m",
                },
                {
                    "name": "Soti Khola River Camp",
                    "location": "Soti Khola",
                    "style": "Riverside teahouse",
                    "price_per_night": 2800,
                    "perk": "Lush sub-tropical forest entry point to the circuit",
                },
            ],
            # 5 — Upper Mustang
            5: [
                {
                    "name": "Hotel Monalisa",
                    "location": "Lo Manthang",
                    "style": "Heritage hotel",
                    "price_per_night": 9500,
                    "perk": "Inside the walled city — rooftop views of the ancient palace",
                },
                {
                    "name": "Lo Manthang Guest House",
                    "location": "Lo Manthang",
                    "style": "Traditional guesthouse",
                    "price_per_night": 7000,
                    "perk": "Tibetan-style rooms with butter-tea breakfast",
                },
                {
                    "name": "Hotel Himalayan Nirvana",
                    "location": "Kagbeni",
                    "style": "Gateway lodge",
                    "price_per_night": 5500,
                    "perk": "Last settlement before the restricted zone checkpoint",
                },
                {
                    "name": "Mustang Holiday Inn",
                    "location": "Jomsom",
                    "style": "Town hotel",
                    "price_per_night": 4800,
                    "perk": "Airport town — hot showers, electricity, and restaurant",
                },
            ],
            # 6 — Gokyo Lakes & Ri
            6: [
                {
                    "name": "Gokyo Resort",
                    "location": "Gokyo",
                    "style": "Lakeside lodge",
                    "price_per_night": 7500,
                    "perk": "Directly beside the 4th sacred Gokyo Lake at 4,790 m",
                },
                {
                    "name": "Hotel Gokyo Namaste",
                    "location": "Gokyo",
                    "style": "Mountain lodge",
                    "price_per_night": 6000,
                    "perk": "Early morning Gokyo Ri sunrise hike from the doorstep",
                },
                {
                    "name": "Machherma Lodge",
                    "location": "Machherma",
                    "style": "Valley teahouse",
                    "price_per_night": 4500,
                    "perk": "Peaceful yak-grazing valley en route to Gokyo",
                },
                {
                    "name": "Dole Guest House",
                    "location": "Dole",
                    "style": "Trail lodge",
                    "price_per_night": 3800,
                    "perk": "First stop above Namche on the Gokyo trail",
                },
            ],
            # 7 — Kanchenjunga Base Camp
            7: [
                {
                    "name": "Kanchenjunga Lodge",
                    "location": "Ghunsa",
                    "style": "Remote mountain lodge",
                    "price_per_night": 5000,
                    "perk": "Last major settlement before the high camps on the north side",
                },
                {
                    "name": "Taplejung Guesthouse",
                    "location": "Taplejung",
                    "style": "Town guesthouse",
                    "price_per_night": 3500,
                    "perk": "Starting point with easy jeep and flight connections",
                },
                {
                    "name": "Yamphudin Village Lodge",
                    "location": "Yamphudin",
                    "style": "Rai homestay lodge",
                    "price_per_night": 2800,
                    "perk": "Authentic Rai culture and home-cooked meals",
                },
                {
                    "name": "Selele Camp Shelter",
                    "location": "Selele",
                    "style": "High camp shelter",
                    "price_per_night": 3200,
                    "perk": "Panoramic Kanchenjunga massif views at 4,290 m",
                },
            ],
            # 8 — Mardi Himal
            8: [
                {
                    "name": "Forest Camp Lodge",
                    "location": "Forest Camp (2,520 m)",
                    "style": "Forest teahouse",
                    "price_per_night": 4000,
                    "perk": "Surrounded by rhododendron forests with Machapuchare glimpses",
                },
                {
                    "name": "Low Camp Guesthouse",
                    "location": "Low Camp (2,985 m)",
                    "style": "Mountain teahouse",
                    "price_per_night": 4500,
                    "perk": "Unobstructed Annapurna South and Hiunchuli views",
                },
                {
                    "name": "High Camp Lodge",
                    "location": "High Camp (3,580 m)",
                    "style": "High-altitude teahouse",
                    "price_per_night": 5000,
                    "perk": "Closest lodge to Mardi Himal Base Camp; spectacular dawn views",
                },
                {
                    "name": "Hotel Siddhartha Kande",
                    "location": "Kande",
                    "style": "Trailhead hotel",
                    "price_per_night": 3200,
                    "perk": "Easy jeep ride from Pokhara; ideal first and last night base",
                },
            ],
            # 9 — Poon Hill Trek
            9: [
                {
                    "name": "Hotel Himalaya Ghorepani",
                    "location": "Ghorepani",
                    "style": "Mountain lodge",
                    "price_per_night": 5500,
                    "perk": "10-minute walk to Poon Hill viewpoint at 3,210 m",
                },
                {
                    "name": "Moonlight Guest House",
                    "location": "Ghorepani",
                    "style": "Comfortable guesthouse",
                    "price_per_night": 4500,
                    "perk": "Cosy dining room with Dhaulagiri and Annapurna panoramas",
                },
                {
                    "name": "New Deurali Guest House",
                    "location": "Ulleri",
                    "style": "Hillside teahouse",
                    "price_per_night": 3000,
                    "perk": "Classic stone staircase village stop with Annapurna views",
                },
                {
                    "name": "Nayapul Riverside Inn",
                    "location": "Nayapul",
                    "style": "Trailhead guesthouse",
                    "price_per_night": 2500,
                    "perk": "Bus and jeep connections directly to Pokhara",
                },
            ],
            # 10 — Gosaikunda Lake
            10: [
                {
                    "name": "Gosaikunda Lake Lodge",
                    "location": "Gosaikunda (4,380 m)",
                    "style": "Sacred lake lodge",
                    "price_per_night": 5500,
                    "perk": "Beside the holy lake — spiritual Janai Purnima festival site",
                },
                {
                    "name": "Lauribina Pass Lodge",
                    "location": "Lauribina Yak (4,610 m)",
                    "style": "High-pass lodge",
                    "price_per_night": 4800,
                    "perk": "Highest teahouse on the route; yak-dung heater included",
                },
                {
                    "name": "Chandanbari Lodge",
                    "location": "Chandanbari",
                    "style": "Ridge teahouse",
                    "price_per_night": 3800,
                    "perk": "Gateway to the Langtang-Helambu crossover route",
                },
                {
                    "name": "Hotel Green Hill Dhunche",
                    "location": "Dhunche",
                    "style": "Town hotel",
                    "price_per_night": 3200,
                    "perk": "Langtang NP headquarters town with bus access from Kathmandu",
                },
            ],
            # 11 — Rara Lake Wilderness
            11: [
                {
                    "name": "Rara Lake Resort",
                    "location": "Rara Lake",
                    "style": "Lakeside resort",
                    "price_per_night": 8000,
                    "perk": "Only permanent accommodation at Nepal's largest lake (2,990 m)",
                },
                {
                    "name": "Murma Guesthouse",
                    "location": "Murma",
                    "style": "Village lodge",
                    "price_per_night": 3000,
                    "perk": "Traditional Thakuri hospitality near the park entry",
                },
                {
                    "name": "Hotel Karnali Jumla",
                    "location": "Jumla",
                    "style": "Town hotel",
                    "price_per_night": 4500,
                    "perk": "Airport town base — apple orchards and apple brandy on tap",
                },
                {
                    "name": "Talcha Airstrip Guesthouse",
                    "location": "Talcha",
                    "style": "Airstrip lodge",
                    "price_per_night": 2800,
                    "perk": "STOL airstrip access; escape hatch if weather closes in",
                },
            ],
            # 12 — Makalu Base Camp
            12: [
                {
                    "name": "Makalu Barun Lodge",
                    "location": "Num",
                    "style": "Trailhead lodge",
                    "price_per_night": 4000,
                    "perk": "Entry point to Makalu Barun National Park",
                },
                {
                    "name": "Seduwa Village Lodge",
                    "location": "Seduwa",
                    "style": "Rai village teahouse",
                    "price_per_night": 3200,
                    "perk": "Lush terraced fields and Arun River gorge views",
                },
                {
                    "name": "Mumbuk Camp",
                    "location": "Mumbuk",
                    "style": "Riverside camp lodge",
                    "price_per_night": 3800,
                    "perk": "Key acclimatisation stop in the Barun River valley",
                },
                {
                    "name": "Makalu Base Camp Shelter",
                    "location": "Makalu Base Camp (4,870 m)",
                    "style": "High camp shelter",
                    "price_per_night": 5500,
                    "perk": "Stone shelter at the base of the world's 5th highest peak",
                },
            ],
            # 13 — Upper Dolpo Wilderness
            13: [
                {
                    "name": "Hotel Dolpo Trout",
                    "location": "Dunai",
                    "style": "District headquarters hotel",
                    "price_per_night": 4500,
                    "perk": "Famous local trout and Barbung Khola riverside setting",
                },
                {
                    "name": "Shey Phoksundo Lodge",
                    "location": "Phoksundo Lake",
                    "style": "Sacred lake lodge",
                    "price_per_night": 5500,
                    "perk": "Nepal's deepest lake at 3,611 m; turquoise glacial water",
                },
                {
                    "name": "Ringmo Village Guesthouse",
                    "location": "Ringmo",
                    "style": "Bon-culture homestay",
                    "price_per_night": 3800,
                    "perk": "Ancient Bon monastery village on the Phoksundo Lake shore",
                },
                {
                    "name": "Shey Gompa Camp",
                    "location": "Shey Gompa",
                    "style": "Monastery camp",
                    "price_per_night": 4200,
                    "perk": "Crystal Mountain pilgrimage site at 4,360 m",
                },
            ],
            # 14 — Nar Phu Valley
            14: [
                {
                    "name": "Nar Village Lodge",
                    "location": "Nar",
                    "style": "Hidden valley lodge",
                    "price_per_night": 5000,
                    "perk": "One of Nepal's most isolated villages at 4,110 m",
                },
                {
                    "name": "Phu Gaon Guesthouse",
                    "location": "Phu",
                    "style": "Tibetan-culture lodge",
                    "price_per_night": 4800,
                    "perk": "Ancient walled village near Himlung Himal base",
                },
                {
                    "name": "Kyang Camp",
                    "location": "Kyang",
                    "style": "Shepherd shelter",
                    "price_per_night": 3500,
                    "perk": "Wild yak territory with views of Pisang Peak",
                },
                {
                    "name": "Meta Village Teahouse",
                    "location": "Meta",
                    "style": "Entry-point teahouse",
                    "price_per_night": 3200,
                    "perk": "First settlement after the Nar Phu restricted area checkpoint",
                },
            ],
            # 15 — Everest Three Passes
            15: [
                {
                    "name": "Kongma La Pass Lodge",
                    "location": "Chhukung",
                    "style": "High-altitude lodge",
                    "price_per_night": 6500,
                    "perk": "Base for Kongma La (5,535 m) and Island Peak climbers",
                },
                {
                    "name": "Renjo La View Lodge",
                    "location": "Lungden",
                    "style": "Remote lodge",
                    "price_per_night": 5500,
                    "perk": "Quiet valley before the Renjo La (5,360 m) ascent",
                },
                {
                    "name": "Cho La Camp House",
                    "location": "Dzongla",
                    "style": "Glacier-approach lodge",
                    "price_per_night": 5800,
                    "perk": "Last stop before crossing the glaciated Cho La (5,420 m)",
                },
                {
                    "name": "Hotel Everest View",
                    "location": "Namche Bazaar",
                    "style": "Boutique mountain hotel",
                    "price_per_night": 12000,
                    "perk": "Luxury recovery base between passes with guaranteed Everest views",
                },
            ],
            # 16 — Annapurna Base Camp
            16: [
                {
                    "name": "Hotel Annapurna Guest House",
                    "location": "Annapurna Base Camp (4,130 m)",
                    "style": "Base camp lodge",
                    "price_per_night": 6500,
                    "perk": "Inside the Annapurna Sanctuary — 360° glacier and peak views",
                },
                {
                    "name": "Machhapuchhre Base Camp Lodge",
                    "location": "MBC (3,700 m)",
                    "style": "High-altitude teahouse",
                    "price_per_night": 5500,
                    "perk": "Iconic Fishtail Mountain directly overhead at sunset",
                },
                {
                    "name": "Deurali Mountain Lodge",
                    "location": "Deurali (3,230 m)",
                    "style": "Ridge teahouse",
                    "price_per_night": 4500,
                    "perk": "Above the Modi Khola gorge; dramatic cloud inversions",
                },
                {
                    "name": "Hotel Himalayas Chhomrong",
                    "location": "Chhomrong (2,170 m)",
                    "style": "Gurung village lodge",
                    "price_per_night": 4000,
                    "perk": "Terraced Gurung village with hot showers and apple pie",
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

            import secrets
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            smtp_user = current_app.config.get("MAIL_USERNAME", "")
            smtp_pass = current_app.config.get("MAIL_PASSWORD", "")

            if not smtp_user or not smtp_pass or smtp_pass == "your-gmail-app-password-here":
                flash("Email service is not configured. Please contact the administrator.", "error")
                return render_template("forgot_password.html", email=email, submitted_email=submitted_email)

            init_db(current_app)
            user = BaseModel.get_user_by_email(email)
            if not user:
                flash("No account found with that email address.", "error")
                return render_template("forgot_password.html", email=email, submitted_email=submitted_email)

            try:
                token = secrets.token_urlsafe(32)
                BaseModel.save_reset_token(email, token)

                reset_url = url_for("auth.reset_password", token=token, _external=True)

                msg = MIMEMultipart("alternative")
                msg["Subject"] = "Ghumna Jam — Password Reset"
                msg["From"] = smtp_user
                msg["To"] = email

                html_body = f"""
                <p>Hello {user['full_name']},</p>
                <p>Click the link below to reset your Ghumna Jam password. This link expires in <strong>1 hour</strong>.</p>
                <p><a href="{reset_url}" style="background:#03231C;color:#F5C647;padding:10px 20px;text-decoration:none;border-radius:6px;font-weight:bold;">Reset My Password</a></p>
                <p>Or copy this URL:<br><code>{reset_url}</code></p>
                <p>If you did not request this, ignore this email.</p>
                <p>— Ghumna Jam Team</p>
                """
                msg.attach(MIMEText(html_body, "html"))

                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(smtp_user, email, msg.as_string())

                flash("Password reset link sent! Check your inbox (and spam folder).", "success")

            except smtplib.SMTPAuthenticationError:
                flash("Email authentication failed. Check MAIL_PASSWORD in config.", "error")
            except Exception as e:
                current_app.logger.error(f"Password reset email error: {e}")
                flash("Could not send reset email. Please try again later.", "error")
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
        price = float(destination.get("price_per_person", 0))
        duration = int(destination.get("duration_days", 1))

        # Per-destination permit costs
        permit_map = {
            1: 7500, 2: 4500, 3: 3500, 4: 9000, 5: 50000,
            6: 7500, 7: 12000, 8: 3000, 9: 3000, 10: 3500,
            11: 15000, 12: 12000, 13: 60000, 14: 10000, 15: 8000, 16: 4000,
        }
        transport_map = {
            1: 18000, 2: 8000, 3: 6000, 4: 12000, 5: 15000,
            6: 18000, 7: 25000, 8: 5000, 9: 5000, 10: 6000,
            11: 22000, 12: 28000, 13: 30000, 14: 20000, 15: 18000, 16: 5000,
        }
        equip_map = {
            1: 8000, 2: 6000, 3: 4000, 4: 8000, 5: 6000,
            6: 8000, 7: 10000, 8: 3000, 9: 3000, 10: 4000,
            11: 5000, 12: 9000, 13: 10000, 14: 7000, 15: 8000, 16: 3000,
        }
        permit_cost   = permit_map.get(dest_id, 4000)
        transport_cost = transport_map.get(dest_id, 6000)
        equip_cost    = equip_map.get(dest_id, 4000)
        guide_cost    = 2500 * duration
        tax           = round(price * 0.13)
        grand_total   = round(price + guide_cost + permit_cost + transport_cost + equip_cost + tax)

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
            permit_cost=permit_cost,
            transport_cost=transport_cost,
            equip_cost=equip_cost,
            guide_cost=guide_cost,
            grand_total=grand_total,
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
        import json as _json
        user_id = session["user_id"]

        if request.method == "POST":
            title       = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            log_data    = request.form.get("log_data", "")

            if title and log_data:
                try:
                    points = _json.loads(log_data)
                    if not isinstance(points, list) or len(points) == 0:
                        raise ValueError("empty")

                    # Compute stats
                    total_dist = 0.0
                    for i in range(1, len(points)):
                        p1, p2 = points[i-1], points[i]
                        import math
                        R = 6371
                        dLat = math.radians(p2["lat"] - p1["lat"])
                        dLon = math.radians(p2["lng"] - p1["lng"])
                        a = math.sin(dLat/2)**2 + math.cos(math.radians(p1["lat"])) * math.cos(math.radians(p2["lat"])) * math.sin(dLon/2)**2
                        total_dist += R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

                    max_alt = max((p.get("alt") or 0) for p in points)
                    speeds  = [p.get("speed") or 0 for p in points if p.get("speed")]
                    avg_spd = (sum(speeds) / len(speeds) * 3.6) if speeds else 0

                    t_start = points[0].get("timestamp", 0) / 1000
                    t_end   = points[-1].get("timestamp", 0) / 1000
                    duration = int(t_end - t_start) if t_end > t_start else 0

                    init_db(current_app)
                    db = get_db()
                    with db.cursor() as cur:
                        cur.execute("""
                            INSERT INTO trek_tracking_sessions
                              (user_id, title, total_distance_km, total_duration_seconds,
                               max_altitude_meters, avg_speed_kmh)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (user_id, title, round(total_dist, 3), duration,
                              int(max_alt), round(avg_spd, 2)))
                        session_id = cur.lastrowid

                        # Save individual GPS points
                        if hasattr(BaseModel, '_get_db'):
                            try:
                                for p in points:
                                    cur.execute("""
                                        INSERT INTO gps_route_points (session_id, latitude, longitude, altitude, speed, recorded_at)
                                        VALUES (%s, %s, %s, %s, %s, FROM_UNIXTIME(%s))
                                    """, (session_id, p["lat"], p["lng"],
                                          p.get("alt"), p.get("speed"),
                                          p.get("timestamp", 0) / 1000))
                            except Exception:
                                pass  # gps_route_points columns may differ
                    db.commit()
                    flash("Trail saved successfully!", "success")
                except Exception as exc:
                    current_app.logger.error(f"Trail save error: {exc}")
                    flash("Could not save trail. Please try again.", "error")
            else:
                flash("Please enter a title and record some trail points first.", "error")

            return redirect(url_for("auth.tracking"))

        # GET — load history
        init_db(current_app)
        history = []
        bookings = []
        try:
            db = get_db()
            with db.cursor() as cur:
                cur.execute("""
                    SELECT id, title, total_distance_km, total_duration_seconds,
                           max_altitude_meters, avg_speed_kmh, created_at
                    FROM trek_tracking_sessions
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT 20
                """, (user_id,))
                history = cur.fetchall()

            bookings = BaseModel.get_bookings_by_user(user_id) or []
        except Exception as exc:
            current_app.logger.error(f"Tracking history load error: {exc}")

        return render_template("tracking.html", history=history, bookings=bookings)

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
