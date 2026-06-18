import pymysql
import secrets
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash

from app.models.database import get_db


class BaseModel:
    @staticmethod
    def get_user_by_email(email):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id,
                    full_name,
                    email,
                    password_hash,
                    phone_number,
                    date_of_birth,
                    profile_picture_url,
                    emergency_contact_name,
                    emergency_contact_phone
                FROM users
                WHERE email = %s
                """,
                (email,),
            )
            return cursor.fetchone()

    @staticmethod
    def authenticate_user(email, password):
        user = BaseModel.get_user_by_email(email)
        if user is None:
            return None

        if not check_password_hash(user["password_hash"], password):
            return None

        return user

    @staticmethod
    def get_user_by_id(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id,
                    full_name,
                    email,
                    password_hash,
                    phone_number,
                    date_of_birth,
                    profile_picture_url,
                    emergency_contact_name,
                    emergency_contact_phone,
                    reset_token,
                    reset_token_expires
                FROM users
                WHERE id = %s
                """,
                (user_id,),
            )
            return cursor.fetchone()

    @staticmethod
    def generate_password_reset_token(email):
        db = get_db()
        token = None
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id FROM users WHERE email = %s
                """,
                (email,),
            )
            user = cursor.fetchone()
            if user:
                token = secrets.token_urlsafe(32)
                expires = datetime.utcnow() + timedelta(hours=1)
                cursor.execute(
                    """
                    UPDATE users
                    SET reset_token = %s,
                        reset_token_expires = %s
                    WHERE id = %s
                    """,
                    (token, expires.strftime("%Y-%m-%d %H:%M:%S"), user["id"]),
                )
                db.commit()
        return token

    @staticmethod
    def get_user_by_reset_token(token):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id,
                    full_name,
                    email,
                    reset_token_expires
                FROM users
                WHERE reset_token = %s
                """,
                (token,),
            )
            user = cursor.fetchone()
            if not user:
                return None
            expires = user.get("reset_token_expires")
            if expires is None or expires < datetime.utcnow():
                return None
            return user

    @staticmethod
    def update_user(
        user_id,
        full_name,
        email,
        phone_number=None,
        date_of_birth=None,
        profile_picture_url=None,
        emergency_contact_name=None,
        emergency_contact_phone=None,
        password=None,
    ):
        db = get_db()

        try:
            with db.cursor() as cursor:
                if password:
                    cursor.execute(
                        """
                        UPDATE users
                        SET full_name = %s,
                            email = %s,
                            phone_number = %s,
                            date_of_birth = %s,
                            profile_picture_url = %s,
                            emergency_contact_name = %s,
                            emergency_contact_phone = %s,
                            password_hash = %s,
                            reset_token = NULL,
                            reset_token_expires = NULL
                        WHERE id = %s
                        """,
                        (
                            full_name,
                            email,
                            phone_number,
                            date_of_birth or None,
                            profile_picture_url,
                            emergency_contact_name,
                            emergency_contact_phone,
                            generate_password_hash(password),
                            user_id,
                        ),
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE users
                        SET full_name = %s,
                            email = %s,
                            phone_number = %s,
                            date_of_birth = %s,
                            profile_picture_url = %s,
                            emergency_contact_name = %s,
                            emergency_contact_phone = %s,
                            reset_token = NULL,
                            reset_token_expires = NULL
                        WHERE id = %s
                        """,
                        (
                            full_name,
                            email,
                            phone_number,
                            date_of_birth or None,
                            profile_picture_url,
                            emergency_contact_name,
                            emergency_contact_phone,
                            user_id,
                        ),
                    )
            db.commit()
        except pymysql.err.IntegrityError as exc:
            db.rollback()
            if exc.args and exc.args[0] == 1062:
                raise ValueError("That email is already used by another account.") from exc
            raise

    @staticmethod
    def update_password(user_id, password):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users
                SET password_hash = %s,
                    reset_token = NULL,
                    reset_token_expires = NULL
                WHERE id = %s
                """,
                (generate_password_hash(password), user_id),
            )
        db.commit()

    @staticmethod
    def create_user(full_name, email, password):
        db = get_db()
        password_hash = generate_password_hash(password)

        try:
            with db.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (full_name, email, password_hash)
                    VALUES (%s, %s, %s)
                    """,
                    (full_name, email, password_hash),
                )
            db.commit()
        except pymysql.err.IntegrityError as exc:
            db.rollback()
            if exc.args and exc.args[0] == 1062:
                raise ValueError("An account with this email already exists.") from exc
            raise

    @staticmethod
    def create_destination(
        name,
        image_url,
        difficulty,
        duration_days,
        season,
        description,
        price_per_person,
        altitude_meters,
        highlights,
    ):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO destinations (
                    name,
                    image_url,
                    difficulty,
                    duration_days,
                    season,
                    description,
                    price_per_person,
                    altitude_meters,
                    highlights
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    name,
                    image_url,
                    difficulty,
                    duration_days,
                    season,
                    description,
                    price_per_person,
                    altitude_meters,
                    highlights,
                ),
            )
        db.commit()

    @staticmethod
    def create_booking(
        user_id,
        destination_id,
        destination_name,
        destination_image_url,
        departure_date,
        travelers_count,
        duration_days,
        difficulty,
        selected_hotel,
        status,
        total_price,
    ):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO bookings (
                    user_id,
                    destination_id,
                    destination_name,
                    destination_image_url,
                    departure_date,
                    travelers_count,
                    duration_days,
                    difficulty,
                    selected_hotel,
                    booking_status,
                    total_price
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    destination_id,
                    destination_name,
                    destination_image_url,
                    departure_date,
                    travelers_count,
                    duration_days,
                    difficulty,
                    selected_hotel,
                    status,
                    total_price,
                ),
            )
        db.commit()

    @staticmethod
    def get_user_bookings(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    destination_id,
                    destination_name AS dest_name,
                    destination_image_url AS dest_image,
                    booking_status AS status,
                    DATE_FORMAT(departure_date, '%%Y-%%m-%%d') AS departure_date,
                    travelers_count,
                    duration_days,
                    difficulty,
                    selected_hotel,
                    total_price,
                    DATE_FORMAT(created_at, '%%Y-%%m-%%d') AS booked_at
                FROM bookings
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def cancel_booking(user_id, booking_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE bookings
                SET booking_status = 'Cancelled'
                WHERE id = %s AND user_id = %s
                """,
                (booking_id, user_id),
            )
        db.commit()

    @staticmethod
    def get_all_destinations(search=None, difficulty=None, season=None):
        db = get_db()
        query = [
            "SELECT d.id, d.name, d.image_url, d.difficulty, d.duration_days, d.season, d.description, d.price_per_person, d.altitude_meters, d.highlights, COALESCE(AVG(r.rating), 0) AS average_rating, COUNT(r.id) AS review_count FROM destinations d LEFT JOIN reviews r ON d.id = r.destination_id"
        ]
        params = []
        conditions = []

        if search:
            conditions.append("LOWER(d.name) LIKE %s")
            params.append(f"%{search.lower()}%")

        if difficulty and difficulty.lower() != "all":
            conditions.append("LOWER(d.difficulty) = %s")
            params.append(difficulty.lower())

        if season and season.lower() != "all":
            conditions.append("LOWER(d.season) LIKE %s")
            params.append(f"%{season.lower()}%")

        if conditions:
            query.append("WHERE " + " AND ".join(conditions))

        query.append("GROUP BY d.id, d.name, d.image_url, d.difficulty, d.duration_days, d.season, d.description, d.price_per_person, d.altitude_meters, d.highlights")
        query.append("ORDER BY d.created_at DESC")

        with db.cursor() as cursor:
            cursor.execute("\n".join(query), tuple(params))
            return cursor.fetchall()

    @staticmethod
    def get_destination_by_id(dest_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, image_url, difficulty, duration_days, season, description, price_per_person, altitude_meters, highlights
                FROM destinations
                WHERE id = %s
                """,
                (dest_id,),
            )
            return cursor.fetchone()

    @staticmethod
    def get_destinations_by_ids(destination_ids):
        if not destination_ids:
            return []

        db = get_db()
        placeholders = ", ".join(["%s"] * len(destination_ids))
        with db.cursor() as cursor:
            cursor.execute(
                f"SELECT id, name, image_url, difficulty, duration_days, season, description, price_per_person, altitude_meters, highlights FROM destinations WHERE id IN ({placeholders})",
                tuple(destination_ids),
            )
            return cursor.fetchall()

    @staticmethod
    def get_favorite_destination_ids(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT destination_id
                FROM favorite_destinations
                WHERE user_id = %s
                """,
                (user_id,),
            )
            return [row["destination_id"] for row in cursor.fetchall()]

    @staticmethod
    def add_favorite_destination(user_id, destination_id):
        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT IGNORE INTO favorite_destinations (user_id, destination_id)
                    VALUES (%s, %s)
                    """,
                    (user_id, destination_id),
                )
            db.commit()
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def remove_favorite_destination(user_id, destination_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM favorite_destinations
                WHERE user_id = %s AND destination_id = %s
                """,
                (user_id, destination_id),
            )
        db.commit()

    @staticmethod
    def get_user_favorites(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT d.id, d.name, d.image_url, d.difficulty, d.duration_days, d.season, d.price_per_person
                FROM destinations d
                INNER JOIN favorite_destinations f ON d.id = f.destination_id
                WHERE f.user_id = %s
                ORDER BY f.created_at DESC
                """,
                (user_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def add_destination_review(user_id, destination_id, rating, comment):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO reviews (user_id, destination_id, rating, comment)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, destination_id, rating, comment),
            )
        db.commit()

    @staticmethod
    def get_reviews_for_destination(destination_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT r.id, r.rating, r.comment, DATE_FORMAT(r.created_at, '%%Y-%%m-%%d') AS created_at, u.full_name
                FROM reviews r
                JOIN users u ON r.user_id = u.id
                WHERE r.destination_id = %s
                ORDER BY r.created_at DESC
                """,
                (destination_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def get_average_rating_for_destination(destination_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT AVG(rating) AS average_rating, COUNT(*) AS review_count
                FROM reviews
                WHERE destination_id = %s
                """,
                (destination_id,),
            )
            return cursor.fetchone()

    @staticmethod
    def save_trail_log(user_id, title, description, log_data):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO trails (user_id, title, description, log_data)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, title, description, log_data),
            )
        db.commit()

    @staticmethod
    def get_user_trails(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, description, DATE_FORMAT(created_at, '%%Y-%%m-%%d') AS saved_at
                FROM trails
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            return cursor.fetchall()
