from datetime import date, timedelta

from app.db import execute_query


def signup(client, email="maya@example.com", password="password123"):
    return client.post(
        "/signup",
        data={
            "name": "Maya Sherpa",
            "email": email,
            "password": password,
            "agree_terms": "yes",
        },
        follow_redirects=True,
    )


def login(client, email="maya@example.com", password="password123"):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def test_home_lists_seeded_destinations(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Featured Destinations" in response.data
    assert b"Mardi Himal" in response.data


def test_signup_rejects_short_password(client):
    response = signup(client, password="short")

    assert response.status_code == 200
    assert b"Password must be at least 8 characters" in response.data


def test_login_rejects_external_next_redirect(client):
    signup(client)
    response = client.post(
        "/login?next=https://example.com/phish",
        data={"email": "maya@example.com", "password": "password123"},
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_compare_requires_two_destinations(client):
    response = client.get("/compare?ids=1", follow_redirects=True)

    assert response.status_code == 200
    assert b"Please select at least two destinations" in response.data


def test_booking_create_and_cancel(client):
    signup(client)
    login(client)
    departure = (date.today() + timedelta(days=30)).isoformat()

    response = client.post(
        "/book/1",
        data={"departure_date": departure, "travelers_count": "2"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"confirmed" in response.data.lower()

    bookings = execute_query("SELECT id, status, travelers_count FROM bookings")
    assert bookings[0]["status"] == "Confirmed"
    assert bookings[0]["travelers_count"] == 2

    cancel_response = client.post(
        f"/bookings/{bookings[0]['id']}/cancel",
        follow_redirects=True,
    )

    assert cancel_response.status_code == 200
    assert b"cancelled" in cancel_response.data.lower()
    cancelled = execute_query("SELECT status FROM bookings WHERE id = ?", (bookings[0]["id"],))
    assert cancelled[0]["status"] == "Cancelled"
