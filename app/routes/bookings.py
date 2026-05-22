from flask import Blueprint, render_template, redirect, url_for, request, session, flash, abort
from app.db import execute_query

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route("/destination/<int:dest_id>")
def destination_detail(dest_id):
    # Fetch destination from database
    results = execute_query("SELECT * FROM destinations WHERE id = ?", (dest_id,))
    if not results:
        abort(404)
    
    destination = results[0]
    return render_template("destination_detail.html", destination=destination)

@bookings_bp.route("/book/<int:dest_id>", methods=["POST"])
def book_trip(dest_id):
    # Enforce login
    if 'user_id' not in session:
        flash("You must be logged in to book a trip.", "error")
        return redirect(url_for('auth.login', next=url_for('bookings.destination_detail', dest_id=dest_id)))
        
    results = execute_query("SELECT * FROM destinations WHERE id = ?", (dest_id,))
    if not results:
        abort(404)
    destination = results[0]
    
    departure_date = request.form.get("departure_date")
    travelers_count_str = request.form.get("travelers_count")
    
    if not departure_date or not travelers_count_str:
        flash("Departure date and number of travelers are required.", "error")
        return redirect(url_for('bookings.destination_detail', dest_id=dest_id))
        
    try:
        travelers_count = int(travelers_count_str)
        if travelers_count < 1:
            raise ValueError()
    except ValueError:
        flash("Please enter a valid number of travelers (at least 1).", "error")
        return redirect(url_for('bookings.destination_detail', dest_id=dest_id))
        
    total_price = destination['price_per_person'] * travelers_count
    user_id = session['user_id']
    
    try:
        execute_query(
            "INSERT INTO bookings (user_id, destination_id, departure_date, travelers_count, total_price, status) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, dest_id, departure_date, travelers_count, total_price, 'Confirmed'),
            commit=True
        )
        flash(f"Success! Your booking for {destination['name']} has been confirmed.", "success")
        return redirect(url_for('bookings.my_bookings'))
    except Exception as e:
        flash(f"An error occurred while creating your booking: {e}", "error")
        return redirect(url_for('bookings.destination_detail', dest_id=dest_id))

@bookings_bp.route("/my-bookings")
def my_bookings():
    # Enforce login
    if 'user_id' not in session:
        flash("Please log in to view your bookings.", "error")
        return redirect(url_for('auth.login', next=url_for('bookings.my_bookings')))
        
    user_id = session['user_id']
    
    # Query bookings with destination details joined
    query = """
    SELECT b.id, b.departure_date, b.travelers_count, b.total_price, b.status, b.booked_at,
           d.name as dest_name, d.image_url as dest_image, d.duration_days, d.difficulty
    FROM bookings b
    JOIN destinations d ON b.destination_id = d.id
    WHERE b.user_id = ?
    ORDER BY b.booked_at DESC
    """
    my_bookings_list = execute_query(query, (user_id,))
    
    return render_template("bookings.html", bookings=my_bookings_list)
