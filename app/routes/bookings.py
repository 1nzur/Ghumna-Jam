from datetime import date

from flask import Blueprint, render_template, redirect, url_for, request, session, flash, abort
from app.db import execute_query

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route("/compare")
def compare_destinations():
    ids_param = request.args.get("ids", "")
    destination_ids = []

    for raw_id in ids_param.split(","):
        raw_id = raw_id.strip()
        if raw_id.isdigit():
            destination_ids.append(int(raw_id))

    # Keep comparisons readable and avoid very large query strings.
    destination_ids = list(dict.fromkeys(destination_ids))[:4]

    if len(destination_ids) < 2:
        flash("Please select at least two destinations to compare.", "error")
        return redirect(url_for('main.home') + "#destinations")

    placeholders = ",".join(["?"] * len(destination_ids))
    destinations = execute_query(
        f"SELECT * FROM destinations WHERE id IN ({placeholders})",
        tuple(destination_ids)
    )
    destinations_by_id = {destination["id"]: destination for destination in destinations}
    ordered_destinations = [
        destinations_by_id[destination_id]
        for destination_id in destination_ids
        if destination_id in destinations_by_id
    ]

    if len(ordered_destinations) < 2:
        flash("Could not find enough destinations to compare.", "error")
        return redirect(url_for('main.home') + "#destinations")

    best_price = min(destination["price_per_person"] for destination in ordered_destinations)
    shortest_duration = min(destination["duration_days"] for destination in ordered_destinations)
    return render_template(
        "compare.html",
        destinations=ordered_destinations,
        best_price=best_price,
        shortest_duration=shortest_duration,
    )

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
        selected_departure = date.fromisoformat(departure_date)
    except ValueError:
        flash("Please choose a valid departure date.", "error")
        return redirect(url_for('bookings.destination_detail', dest_id=dest_id))

    if selected_departure <= date.today():
        flash("Departure date must be in the future.", "error")
        return redirect(url_for('bookings.destination_detail', dest_id=dest_id))
        
    try:
        travelers_count = int(travelers_count_str)
        if travelers_count < 1 or travelers_count > 12:
            raise ValueError()
    except ValueError:
        flash("Please enter a valid number of travelers between 1 and 12.", "error")
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


@bookings_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
def cancel_booking(booking_id):
    if "user_id" not in session:
        flash("Please log in to manage your bookings.", "error")
        return redirect(url_for("auth.login", next=url_for("bookings.my_bookings")))

    booking_rows = execute_query(
        "SELECT id, status FROM bookings WHERE id = ? AND user_id = ?",
        (booking_id, session["user_id"]),
    )
    if not booking_rows:
        abort(404)

    if booking_rows[0]["status"] == "Cancelled":
        flash("That booking is already cancelled.", "error")
        return redirect(url_for("bookings.my_bookings"))

    execute_query(
        "UPDATE bookings SET status = ? WHERE id = ? AND user_id = ?",
        ("Cancelled", booking_id, session["user_id"]),
        commit=True,
    )
    flash("Your booking has been cancelled.", "success")
    return redirect(url_for("bookings.my_bookings"))
