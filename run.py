from flask import Flask, redirect, render_template, url_for
from app.config import Config
from app.db import init_db, execute_query
from app.routes.auth import auth_bp
from app.routes.bookings import bookings_bp

app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)
app.config.from_object(Config)

# Initialize database tables and seed destinations
with app.app_context():
    init_db()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(bookings_bp)

@app.route("/")
def home():
    # Fetch all destinations from the seeded database
    destinations = execute_query("SELECT * FROM destinations")
    return render_template("landpage.html", destinations=destinations)

# Backward-compatibility redirects for old root routes
@app.route("/login")
def old_login():
    return redirect(url_for('auth.login'))

@app.route("/signup")
def old_signup():
    return redirect(url_for('auth.signup'))

@app.route("/edit-profile")
def signup():
    return render_template("edit-profile.html")

if __name__ == "__main__":
    app.run(debug=True, port=5055)
