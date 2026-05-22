from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from app.controllers.ControllerAuth import register_user, authenticate_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    # If user is already logged in, redirect to home
    if 'user_id' in session:
        return redirect(url_for('home'))
        
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
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
        return redirect(url_for('home'))
        
    if request.method == "POST":
        email = request.form.get("email")
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
            flash(f"Welcome back, {user_or_err['name']}!", "success")
            
            # Check if there is a redirect path saved
            next_url = request.args.get('next') or url_for('home')
            return redirect(next_url)
        else:
            flash(user_or_err, "error")
            return render_template("login.html", email=email)
            
    return render_template("login.html")

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    # If user is already logged in, redirect to home
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == "POST":
        email = request.form.get("email")

        if not email:
            flash("Email address is required.", "error")
            return render_template("forgot_password.html", email=email)

        flash("If an account exists for that email, password reset instructions will be sent shortly.", "success")
        return redirect(url_for('auth.login'))

    return render_template("forgot_password.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))
