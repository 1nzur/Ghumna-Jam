from datetime import timedelta
from urllib.parse import urlsplit

from flask import Blueprint, current_app, render_template, redirect, url_for, request, session, flash
from app.controllers.ControllerAuth import register_user, authenticate_user

auth_bp = Blueprint('auth', __name__)


<<<<<<< HEAD
def is_safe_next_url(target):
    if not target:
        return False
    target_ref = urlsplit(target)
    return not target_ref.netloc and target_ref.scheme in ("", "http", "https")
=======
class AuthRoutes:
    def __init__(self):
        self.bp = Blueprint("auth", __name__)
        self.controller = AuthController()
>>>>>>> 0a4586c3a60c2aaf85463b38455a243fc85d4f34


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    # If user is already logged in, redirect to home
    if 'user_id' in session:
        return redirect(url_for('main.home'))
        
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        agree_terms = request.form.get("agree_terms")
        
        if not name or not email or not password:
            flash("All fields are required.", "error")
            return render_template("signup.html", name=name, email=email)
            
        if not agree_terms:
            flash("You must agree to the terms and conditions.", "error")
            return render_template("signup.html", name=name, email=email)
            
        success, message = register_user(name, email, password)
        if success:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('auth.login'))
        else:
            flash(message, "error")
            return render_template("signup.html", name=name, email=email)
            
    return render_template("signup.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # If user is already logged in, redirect to home
    if 'user_id' in session:
        return redirect(url_for('main.home'))
        
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        
        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("login.html", email=email)
            
        success, user_or_err = authenticate_user(email, password)
        if success:
            session.clear()
            session['user_id'] = user_or_err['id']
            session['user_name'] = user_or_err['name']
            session['user_email'] = user_or_err['email']
            session.permanent = bool(request.form.get("remember_me"))
            if session.permanent:
                current_app.permanent_session_lifetime = timedelta(days=14)
            flash(f"Welcome back, {user_or_err['name']}!", "success")
            
            next_url = request.args.get('next')
            if not is_safe_next_url(next_url):
                next_url = url_for('main.home')
            return redirect(next_url)
        else:
            flash(user_or_err, "error")
            return render_template("login.html", email=email)
            
    return render_template("login.html")

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    # If user is already logged in, redirect to home
    if 'user_id' in session:
        return redirect(url_for('main.home'))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if not email:
            flash("Email address is required.", "error")
            return render_template("forgot_password.html", email=email)

        flash("If an account exists for that email, password reset instructions will be sent shortly.", "success")
        return redirect(url_for('auth.login'))

    return render_template("forgot_password.html")

<<<<<<< HEAD
        self.bp.route("/bookings")(
            self.controller.bookings
        )

        self.bp.route("/destination/<int:dest_id>")(
            self.controller.destination_detail
        )
        self.bp.route("/compare")(
            self.controller.compare_treks
        )

        self.bp.route("/book/<int:dest_id>", methods=["POST"])(
            self.controller.book_trip
        )

        self.bp.route("/edit-profile", methods=["GET", "POST"])(
            self.controller.edit_profile
        )

        self.bp.route("/profile", methods=["GET", "POST"])(
            self.controller.edit_profile
        )

        self.bp.route("/tracking")(
            self.controller.tracking
        )

<<<<<<< HEAD
        self.bp.route("/checklist")(
            self.controller.packing_checklist
        )

        self.bp.route("/recommendations")(
            self.controller.recommendations
        )

        return self.bp
=======
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('main.home'))
>>>>>>> 28f10469f5bcc5a4b8bb22c4fcbaf984bdfb08e7
=======
        self.bp.route("/about-us")(
            self.controller.about_us
        )

        self.bp.route("/logout")(
            self.controller.logout
        )

        self.bp.route("/forgot-password", methods=["GET", "POST"])(
            self.controller.forgot_password
        )

        self.bp.route("/bookings")(
            self.controller.bookings
        )

        self.bp.route("/destination/<int:dest_id>")(
            self.controller.destination_detail
        )

        self.bp.route("/book/<int:dest_id>", methods=["POST"])(
            self.controller.book_trip
        )

        self.bp.route("/edit-profile", methods=["GET", "POST"])(
            self.controller.edit_profile
        )

        self.bp.route("/profile", methods=["GET", "POST"])(
            self.controller.edit_profile
        )

        self.bp.route("/badges")(
            self.controller.badges
        )

        self.bp.route("/notifications")(
            self.controller.notifications
        )

        return self.bp
>>>>>>> 0a4586c3a60c2aaf85463b38455a243fc85d4f34
