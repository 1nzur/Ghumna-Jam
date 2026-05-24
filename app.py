import os

import mysql.connector
from flask import Flask, jsonify, request, send_from_directory
from mysql.connector import Error
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__, static_folder=".", static_url_path="")


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "ghumna_jam"),
    )


@app.get("/")
def home():
    return send_from_directory(".", "index.html")


@app.post("/api/bookings")
def create_booking():
    data = request.get_json(silent=True) or {}
    required_fields = ["name", "email", "trek", "date", "people"]
    missing_fields = [field for field in required_fields if not data.get(field)]

    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    try:
        people = int(data["people"])
    except (TypeError, ValueError):
        return jsonify({"error": "Number of trekkers must be a number."}), 400

    if people < 1 or people > 20:
        return jsonify({"error": "Number of trekkers must be between 1 and 20."}), 400

    query = """
        INSERT INTO bookings (full_name, email, trek, preferred_date, people, message)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (
        data["name"],
        data["email"],
        data["trek"],
        data["date"],
        people,
        data.get("message", ""),
    )

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query, values)
        connection.commit()
        booking_id = cursor.lastrowid
    except Error as error:
        return jsonify({"error": f"Database error: {error}"}), 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()

    return jsonify({"booking_id": booking_id}), 201


if __name__ == "__main__":
    app.run(debug=True)
