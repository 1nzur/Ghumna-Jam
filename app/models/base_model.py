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
        group_type=None,
        package_name=None,
        hotel_fee=0,
        transportation_fee=0,
        guide_fee=0,
        permit_fee=0,
        taxes=0,
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
                    group_type,
                    package_name,
                    hotel_fee,
                    transportation_fee,
                    guide_fee,
                    permit_fee,
                    taxes,
                    booking_status,
                    total_price
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                    group_type,
                    package_name,
                    hotel_fee,
                    transportation_fee,
                    guide_fee,
                    permit_fee,
                    taxes,
                    status,
                    total_price,
                ),
            )
            booking_id = cursor.lastrowid
            
            # Insert into trip_history
            cursor.execute(
                """
                INSERT INTO trip_history (user_id, booking_id, destination_id, history_status, start_date, end_date)
                VALUES (%s, %s, %s, %s, %s, DATE_ADD(%s, INTERVAL %s DAY))
                """,
                (user_id, booking_id, destination_id, 'Upcoming', departure_date, departure_date, duration_days)
            )
            
            # Fetch trek pricing details to store exact cost breakdown
            cursor.execute("SELECT * FROM destinations WHERE id = %s", (destination_id,))
            dest = cursor.fetchone()
            if dest:
                package_cost = float(dest["price_per_person"])
                hotel_rate = float(dest["hotel_price_per_night"])
                guide_rate = float(dest["guide_fee_per_day"])
                trans_rate = float(dest["transportation_fee"])
                permit_rate = float(dest["permit_fee"])
                
                nights = max(1, int(duration_days) - 1)
                days = int(duration_days)
                
                trek_package_cost = package_cost * int(travelers_count)
                hotel_cost = hotel_rate * nights * int(travelers_count)
                guide_cost = guide_rate * days
                transportation_cost = float(transportation_fee)
                permit_costs = permit_rate * int(travelers_count)
                
                group_size = int(travelers_count)
                if group_size == 1:
                    group_size_adjustment = 0.10 * trek_package_cost
                elif group_size >= 6:
                    group_size_adjustment = -0.10 * trek_package_cost
                elif group_size >= 3:
                    group_size_adjustment = -0.05 * trek_package_cost
                else:
                    group_size_adjustment = 0.00
                
                cursor.execute(
                    """
                    INSERT INTO cost_breakdown_records (
                        booking_id, user_id, destination_id, trek_package_cost,
                        hotel_cost_per_night, number_of_nights, guide_cost_per_day, number_of_days,
                        transportation_cost, permit_costs, group_size_adjustment, final_total_cost
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        booking_id, user_id, destination_id, trek_package_cost,
                        hotel_rate, nights, guide_rate, days,
                        transportation_cost, permit_costs, group_size_adjustment, total_price
                    )
                )
        db.commit()
        
        # Update statistics
        try:
            BaseModel.update_trek_statistics(destination_id)
            BaseModel.update_user_statistics(user_id)
            BaseModel.award_achievements(user_id)
        except Exception as e:
            print("Error updating statistics during create_booking:", e)

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
                    group_type,
                    package_name,
                    hotel_fee,
                    transportation_fee,
                    guide_fee,
                    permit_fee,
                    taxes,
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
            "SELECT d.id, d.name, d.region, d.image_url, d.difficulty, d.duration_days, d.distance_km, d.season, d.description, d.price_per_person, d.hotel_price_per_night, d.transportation_fee, d.guide_fee_per_day, d.permit_fee, d.altitude_meters, d.highlights, COALESCE(AVG(r.rating), 0) AS average_rating, COUNT(r.id) AS review_count FROM destinations d LEFT JOIN reviews r ON d.id = r.destination_id AND r.status = 'Published'"
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

        query.append("GROUP BY d.id, d.name, d.region, d.image_url, d.difficulty, d.duration_days, d.distance_km, d.season, d.description, d.price_per_person, d.hotel_price_per_night, d.transportation_fee, d.guide_fee_per_day, d.permit_fee, d.altitude_meters, d.highlights")
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
                SELECT id, name, region, image_url, difficulty, duration_days, distance_km, season, description, price_per_person, hotel_price_per_night, transportation_fee, guide_fee_per_day, permit_fee, altitude_meters, highlights
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
                f"SELECT id, name, region, image_url, difficulty, duration_days, distance_km, season, description, price_per_person, hotel_price_per_night, transportation_fee, guide_fee_per_day, permit_fee, altitude_meters, highlights FROM destinations WHERE id IN ({placeholders})",
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
                INSERT INTO reviews (user_id, destination_id, rating, comment, status)
                VALUES (%s, %s, %s, %s, 'Published')
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
                WHERE r.destination_id = %s AND r.status = 'Published'
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
                WHERE destination_id = %s AND status = 'Published'
                """,
                (destination_id,),
            )
            return cursor.fetchone()

    @staticmethod
    def save_trail_log(user_id, title, description, log_data, distance_km=0, duration_seconds=0, elevation_gain_m=0):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO trails (user_id, title, description, log_data, distance_km, duration_seconds, elevation_gain_m)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, title, description, log_data, distance_km, duration_seconds, elevation_gain_m),
            )
        db.commit()

    @staticmethod
    def get_user_trails(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, description, distance_km, duration_seconds, elevation_gain_m, DATE_FORMAT(created_at, '%%Y-%%m-%%d') AS saved_at
                FROM trails
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def save_emergency_alert(user_id, latitude, longitude, accuracy_m, message):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO emergency_alerts (user_id, latitude, longitude, accuracy_m, message)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, latitude, longitude, accuracy_m, message),
            )
        db.commit()

    @staticmethod
    def get_checklist_items(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, item_name, category, is_packed
                FROM checklist_items
                WHERE user_id = %s
                ORDER BY category, created_at
                """,
                (user_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def add_checklist_item(user_id, item_name, category):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO checklist_items (user_id, item_name, category)
                VALUES (%s, %s, %s)
                """,
                (user_id, item_name, category),
            )
        db.commit()

    @staticmethod
    def update_checklist_item(user_id, item_id, is_packed):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE checklist_items
                SET is_packed = %s
                WHERE id = %s AND user_id = %s
                """,
                (1 if is_packed else 0, item_id, user_id),
            )
        db.commit()

    @staticmethod
    def delete_checklist_item(user_id, item_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "DELETE FROM checklist_items WHERE id = %s AND user_id = %s",
                (item_id, user_id),
            )
        db.commit()

    @staticmethod
    def upload_trek_photo(user_id, destination_id, file_path, caption):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO trek_photos (user_id, destination_id, file_path, caption)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, destination_id or None, file_path, caption),
            )
        db.commit()

    @staticmethod
    def get_destination_photos(destination_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.*, u.full_name
                FROM trek_photos p
                JOIN users u ON p.user_id = u.id
                WHERE p.destination_id = %s
                ORDER BY p.created_at DESC
                """,
                (destination_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def get_user_photos(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.*, d.name AS destination_name
                FROM trek_photos p
                LEFT JOIN destinations d ON p.destination_id = d.id
                WHERE p.user_id = %s
                ORDER BY p.created_at DESC
                """,
                (user_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def delete_user_photo(user_id, photo_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "DELETE FROM trek_photos WHERE id = %s AND user_id = %s",
                (photo_id, user_id),
            )
        db.commit()

    @staticmethod
    def add_review_reply(review_id, user_id, body):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO review_replies (review_id, user_id, body)
                VALUES (%s, %s, %s)
                """,
                (review_id, user_id, body),
            )
        db.commit()

    @staticmethod
    def get_replies_for_destination(destination_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT rr.*, u.full_name
                FROM review_replies rr
                JOIN reviews r ON rr.review_id = r.id
                JOIN users u ON rr.user_id = u.id
                WHERE r.destination_id = %s
                ORDER BY rr.created_at
                """,
                (destination_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def get_user_reviews(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT r.*, d.name AS dest_name, d.image_url AS dest_image, d.difficulty
                FROM reviews r
                JOIN destinations d ON r.destination_id = d.id
                WHERE r.user_id = %s
                ORDER BY r.created_at DESC
                """,
                (user_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def update_user_review(user_id, review_id, rating, comment, status):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE reviews
                SET rating = %s, comment = %s, status = %s
                WHERE id = %s AND user_id = %s
                """,
                (rating, comment, status, review_id, user_id),
            )
        db.commit()

    @staticmethod
    def delete_user_review(user_id, review_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "DELETE FROM reviews WHERE id = %s AND user_id = %s",
                (review_id, user_id),
            )
        db.commit()

    @staticmethod
    def get_following_ids(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT following_id FROM follows WHERE follower_id = %s", (user_id,))
            return [row["following_id"] for row in cursor.fetchall()]

    @staticmethod
    def follow_user(follower_id, following_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "INSERT IGNORE INTO follows (follower_id, following_id) VALUES (%s, %s)",
                (follower_id, following_id),
            )
        db.commit()

    @staticmethod
    def unfollow_user(follower_id, following_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "DELETE FROM follows WHERE follower_id = %s AND following_id = %s",
                (follower_id, following_id),
            )
        db.commit()

    @staticmethod
    def list_trekkers(current_user_id, search=None):
        db = get_db()
        params = [current_user_id]
        where = ["u.id <> %s"]
        if search:
            where.append("(LOWER(u.full_name) LIKE %s OR LOWER(u.email) LIKE %s)")
            params.extend([f"%{search.lower()}%", f"%{search.lower()}%"])
        with db.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT u.id, u.full_name, u.email, u.profile_picture_url, COUNT(t.id) AS trek_count
                FROM users u
                LEFT JOIN trails t ON u.id = t.user_id
                WHERE {' AND '.join(where)}
                GROUP BY u.id, u.full_name, u.email, u.profile_picture_url
                ORDER BY trek_count DESC, u.full_name
                """,
                tuple(params),
            )
            return cursor.fetchall()

    @staticmethod
    def get_followers(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT u.id, u.full_name, u.email, u.profile_picture_url
                FROM follows f
                JOIN users u ON f.follower_id = u.id
                WHERE f.following_id = %s
                ORDER BY u.full_name
                """,
                (user_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def get_following(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT u.id, u.full_name, u.email, u.profile_picture_url
                FROM follows f
                JOIN users u ON f.following_id = u.id
                WHERE f.follower_id = %s
                ORDER BY u.full_name
                """,
                (user_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def award_achievements(user_id):
        BaseModel.update_user_statistics(user_id)
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM user_statistics WHERE user_id = %s", (user_id,))
            stats = cursor.fetchone()
            if not stats:
                return
                
            completed_treks = int(stats["completed_treks_count"])
            total_dist = float(stats["total_distance_km"])
            max_alt = int(stats["max_altitude_reached"])
            reviews_count = int(stats["reviews_count"])
            photos_count = int(stats["photos_uploaded_count"])
            followers_count = int(stats["followers_count"])
            
            cursor.execute("SELECT id, slug, threshold_type, threshold_value FROM achievements")
            achievements = cursor.fetchall()
            
            for achievement in achievements:
                t_type = achievement["threshold_type"]
                val = achievement["threshold_value"]
                
                earned = False
                if t_type == "bookings":
                    cursor.execute("SELECT COUNT(*) AS count FROM bookings WHERE user_id = %s AND booking_status = 'Confirmed'", (user_id,))
                    b_count = cursor.fetchone()["count"]
                    earned = (b_count >= val or completed_treks >= val)
                elif t_type == "altitude":
                    earned = (max_alt >= val)
                elif t_type == "distance":
                    earned = (total_dist >= val)
                elif t_type == "reviews":
                    earned = (reviews_count >= val)
                elif t_type == "photos":
                    earned = (photos_count >= val)
                elif t_type == "followers":
                    earned = (followers_count >= val)
                    
                if earned:
                    cursor.execute(
                        "INSERT IGNORE INTO user_achievements (user_id, achievement_id) VALUES (%s, %s)",
                        (user_id, achievement["id"])
                    )
        db.commit()

    @staticmethod
    def get_achievement_progress(user_id):
        BaseModel.award_achievements(user_id)
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM user_statistics WHERE user_id = %s", (user_id,))
            stats = cursor.fetchone()
            if not stats:
                stats = {
                    "total_distance_km": 0.0,
                    "total_duration_hours": 0.0,
                    "completed_treks_count": 0,
                    "max_altitude_reached": 0,
                    "reviews_count": 0,
                    "photos_uploaded_count": 0,
                    "followers_count": 0,
                    "following_count": 0
                }
                
            cursor.execute("SELECT COUNT(*) AS count FROM bookings WHERE user_id = %s AND booking_status = 'Confirmed'", (user_id,))
            bookings_count = cursor.fetchone()["count"]
            completed_count = stats.get("completed_treks_count", 0)
            
            cursor.execute(
                """
                SELECT a.*, ua.earned_at
                FROM achievements a
                LEFT JOIN user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = %s
                ORDER BY a.id
                """,
                (user_id,),
            )
            rows = cursor.fetchall()
            
        for row in rows:
            t_type = row["threshold_type"]
            val = row["threshold_value"]
            
            if t_type == "bookings":
                current = max(bookings_count, completed_count)
            elif t_type == "altitude":
                current = stats.get("max_altitude_reached", 0)
            elif t_type == "distance":
                current = stats.get("total_distance_km", 0.0)
            elif t_type == "reviews":
                current = stats.get("reviews_count", 0)
            elif t_type == "photos":
                current = stats.get("photos_uploaded_count", 0)
            elif t_type == "followers":
                current = stats.get("followers_count", 0)
            else:
                current = 0
                
            row["earned"] = bool(row.get("earned_at"))
            row["progress_value"] = min(float(current or 0), float(val))
            row["progress_total"] = float(val)
            row["progress_percent"] = 100 if val == 0 else int((row["progress_value"] / val) * 100)
            row["icon"] = {
                "first-trek": "★", "five-treks": "5", "ten-treks": "10", "twenty-five-treks": "25",
                "reached-3000m": "▲", "reached-5000m": "▲", "reached-7000m": "▲",
                "travelled-50km": "GPS", "travelled-100km": "GPS", "travelled-500km": "GPS",
                "first-review": "✍", "first-photo": "📷", "first-follower": "👤",
                "ten-followers": "👤", "fifty-followers": "👤"
            }.get(row["slug"], "✓")
            row["color"] = "from-brandGreen to-emerald-700"
            row["requirement_text"] = f"{t_type.capitalize()} milestone: {val}"
            
        earned = [row for row in rows if row["earned"]]
        return completed_count, rows, earned

    # NEW DATABASE IMPLEMENTATIONS FOR NEPAL TREKKING PLATFORM

    @staticmethod
    def update_user_statistics(user_id):
        db = get_db()
        with db.cursor() as cursor:
            # 1. Total distance and duration from trek_tracking_sessions
            cursor.execute(
                """
                SELECT COALESCE(SUM(total_distance_km), 0) AS dist, COALESCE(SUM(total_duration_seconds), 0) AS dur
                FROM trek_tracking_sessions WHERE user_id = %s
                """,
                (user_id,)
            )
            tracking_stats = cursor.fetchone()
            total_dist = float(tracking_stats["dist"])
            total_dur_hours = float(tracking_stats["dur"]) / 3600.0
            
            # 2. Completed treks count from trip_history
            cursor.execute(
                """
                SELECT COUNT(*) AS count FROM trip_history
                WHERE user_id = %s AND history_status = 'Completed'
                """,
                (user_id,)
            )
            completed_count = cursor.fetchone()["count"]
            
            # 3. Max altitude reached
            cursor.execute(
                """
                SELECT COALESCE(MAX(max_altitude_meters), 0) AS max_alt
                FROM trek_tracking_sessions WHERE user_id = %s
                """,
                (user_id,)
            )
            max_alt = cursor.fetchone()["max_alt"]
            
            # 4. Reviews count
            cursor.execute("SELECT COUNT(*) AS count FROM reviews WHERE user_id = %s", (user_id,))
            reviews_count = cursor.fetchone()["count"]
            
            # 5. Photos uploaded count
            cursor.execute("SELECT COUNT(*) AS count FROM trek_photos WHERE user_id = %s", (user_id,))
            photos_count = cursor.fetchone()["count"]
            
            # 6. Followers & Following count
            cursor.execute("SELECT COUNT(*) AS count FROM follows WHERE following_id = %s", (user_id,))
            followers_count = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) AS count FROM follows WHERE follower_id = %s", (user_id,))
            following_count = cursor.fetchone()["count"]
            
            # Insert/Update user_statistics
            cursor.execute(
                """
                INSERT INTO user_statistics (
                    user_id, total_distance_km, total_duration_hours, completed_treks_count,
                    max_altitude_reached, reviews_count, photos_uploaded_count, followers_count, following_count
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    total_distance_km = VALUES(total_distance_km),
                    total_duration_hours = VALUES(total_duration_hours),
                    completed_treks_count = VALUES(completed_treks_count),
                    max_altitude_reached = VALUES(max_altitude_reached),
                    reviews_count = VALUES(reviews_count),
                    photos_uploaded_count = VALUES(photos_uploaded_count),
                    followers_count = VALUES(followers_count),
                    following_count = VALUES(following_count)
                """,
                (
                    user_id, total_dist, total_dur_hours, completed_count,
                    max_alt, reviews_count, photos_count, followers_count, following_count
                )
            )
        db.commit()

    @staticmethod
    def update_trek_statistics(destination_id):
        db = get_db()
        with db.cursor() as cursor:
            # 1. Total bookings
            cursor.execute("SELECT COUNT(*) AS count FROM bookings WHERE destination_id = %s AND booking_status <> 'Cancelled'", (destination_id,))
            bookings_count = cursor.fetchone()["count"]
            
            # 2. Avg rating & Reviews count
            cursor.execute(
                """
                SELECT COALESCE(AVG(rating), 0.00) AS avg_rate, COUNT(*) AS count
                FROM reviews WHERE destination_id = %s AND status = 'Published'
                """,
                (destination_id,)
            )
            review_stats = cursor.fetchone()
            avg_rating = float(review_stats["avg_rate"])
            reviews_count = review_stats["count"]
            
            # 3. Photos count
            cursor.execute("SELECT COUNT(*) AS count FROM trek_photos WHERE destination_id = %s", (destination_id,))
            photos_count = cursor.fetchone()["count"]
            
            # Insert/Update trek_statistics
            cursor.execute(
                """
                INSERT INTO trek_statistics (destination_id, total_bookings, average_rating, reviews_count, photos_count)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    total_bookings = VALUES(total_bookings),
                    average_rating = VALUES(average_rating),
                    reviews_count = VALUES(reviews_count),
                    photos_count = VALUES(photos_count)
                """,
                (destination_id, bookings_count, avg_rating, reviews_count, photos_count)
            )
        db.commit()

    @staticmethod
    def get_trip_history(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT t.*, d.name AS dest_name, d.image_url AS dest_image, d.difficulty, d.duration_days, b.total_price, b.travelers_count
                FROM trip_history t
                JOIN destinations d ON t.destination_id = d.id
                JOIN bookings b ON t.booking_id = b.id
                WHERE t.user_id = %s
                ORDER BY t.created_at DESC
                """,
                (user_id,)
            )
            return cursor.fetchall()

    @staticmethod
    def get_trip_detail(user_id, trip_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT t.id AS trip_id, t.history_status, t.booking_id, t.destination_id,
                       d.name AS dest_name, d.image_url AS dest_image, d.difficulty, d.duration_days,
                       b.total_price, b.travelers_count, b.selected_hotel, b.group_type, b.package_name,
                       b.hotel_fee, b.transportation_fee, b.guide_fee, b.permit_fee, b.taxes,
                       DATE_FORMAT(t.created_at, '%%Y-%%m-%%d') AS booked_at
                FROM trip_history t
                JOIN destinations d ON t.destination_id = d.id
                JOIN bookings b ON t.booking_id = b.id
                WHERE t.user_id = %s AND t.id = %s
                """,
                (user_id, trip_id)
            )
            trip = cursor.fetchone()
            if not trip:
                return None
            
            # Fetch tracking session associated with the trip if exists
            cursor.execute(
                """
                SELECT * FROM trek_tracking_sessions
                WHERE trip_id = %s LIMIT 1
                """,
                (trip_id,)
            )
            session = cursor.fetchone()
            if session:
                trip["tracking_session"] = session
                # Fetch route points
                cursor.execute(
                    """
                    SELECT latitude AS lat, longitude AS lng, altitude AS alt, distance_travelled_km AS dist, elapsed_seconds AS time
                    FROM gps_route_points
                    WHERE session_id = %s
                    ORDER BY id ASC
                    """,
                    (session["id"],)
                )
                trip["route_points"] = cursor.fetchall()
            return trip

    @staticmethod
    def save_tracking_session(user_id, title, distance_km, duration_seconds, elevation_gain_m, points_list):
        db = get_db()
        with db.cursor() as cursor:
            # Find an active upcoming trip to link
            cursor.execute(
                """
                SELECT id FROM trip_history
                WHERE user_id = %s AND history_status = 'Upcoming'
                ORDER BY created_at DESC LIMIT 1
                """,
                (user_id,)
            )
            trip = cursor.fetchone()
            trip_id = trip["id"] if trip else None
            
            max_alt = 0
            if points_list:
                altitudes = [float(p.get("alt") or 0) for p in points_list if p.get("alt") is not None]
                if altitudes:
                    max_alt = max(altitudes)
                    
            avg_speed = 0.0
            if duration_seconds > 0:
                avg_speed = (float(distance_km) / (float(duration_seconds) / 3600.0))
                
            cursor.execute(
                """
                INSERT INTO trek_tracking_sessions (
                    user_id, trip_id, title, total_distance_km,
                    total_duration_seconds, elevation_gain_meters, avg_speed_kmh, max_altitude_meters, end_time
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """,
                (user_id, trip_id, title, distance_km, duration_seconds, elevation_gain_m, avg_speed, max_alt)
            )
            session_id = cursor.lastrowid
            
            dp_points = []
            elev_history = []
            for i, p in enumerate(points_list):
                lat = float(p.get("lat"))
                lng = float(p.get("lng"))
                alt = float(p.get("alt") or 0.0)
                speed = float(p.get("speed") or 0.0)
                acc = float(p.get("acc") or 0.0)
                dist_travelled = 0.0
                if i > 0:
                    dist_travelled = (float(distance_km) / len(points_list)) * i
                elapsed = int(duration_seconds / len(points_list)) * i
                
                dp_points.append((session_id, lat, lng, alt, dist_travelled, elapsed))
                elev_history.append((session_id, alt))
                
            if dp_points:
                cursor.executemany(
                    """
                    INSERT INTO gps_route_points (session_id, latitude, longitude, altitude, distance_travelled_km, elapsed_seconds)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    dp_points
                )
            if elev_history:
                cursor.executemany(
                    """
                    INSERT INTO elevation_history (session_id, altitude)
                    VALUES (%s, %s)
                    """,
                    elev_history
                )
                
            if trip_id:
                cursor.execute(
                    """
                    UPDATE trip_history
                    SET history_status = 'Completed'
                    WHERE id = %s
                    """,
                    (trip_id,)
                )
        db.commit()
        BaseModel.update_user_statistics(user_id)
        BaseModel.award_achievements(user_id)
        return session_id

    @staticmethod
    def get_user_trails(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, total_distance_km AS distance_km, total_duration_seconds AS duration_seconds,
                       elevation_gain_meters AS elevation_gain_m, DATE_FORMAT(created_at, '%%Y-%%m-%%d') AS created_at
                FROM trek_tracking_sessions
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,)
            )
            return cursor.fetchall()

    @staticmethod
    def get_user_checklists(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM packing_checklists WHERE user_id = %s", (user_id,))
            lists = cursor.fetchall()
            if not lists:
                cursor.execute("INSERT INTO packing_checklists (user_id, title) VALUES (%s, 'My Expedition Checklist')", (user_id,))
                db.commit()
                cursor.execute("SELECT * FROM packing_checklists WHERE user_id = %s", (user_id,))
                lists = cursor.fetchall()
            return lists

    @staticmethod
    def get_checklist_items(user_id):
        db = get_db()
        with db.cursor() as cursor:
            lists = BaseModel.get_user_checklists(user_id)
            checklist_id = lists[0]["id"]
            cursor.execute(
                """
                SELECT id, item_name AS name, category, is_packed AS packed
                FROM packing_checklist_items
                WHERE checklist_id = %s
                ORDER BY created_at ASC
                """,
                (checklist_id,)
            )
            return cursor.fetchall()

    @staticmethod
    def add_checklist_item(user_id, item_name, category):
        db = get_db()
        with db.cursor() as cursor:
            lists = BaseModel.get_user_checklists(user_id)
            checklist_id = lists[0]["id"]
            cursor.execute(
                """
                INSERT INTO packing_checklist_items (checklist_id, item_name, category, is_packed)
                VALUES (%s, %s, %s, 0)
                """,
                (checklist_id, item_name, category)
            )
        db.commit()

    @staticmethod
    def update_checklist_item(user_id, item_id, is_packed):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE packing_checklist_items pci
                JOIN packing_checklists pc ON pci.checklist_id = pc.id
                SET pci.is_packed = %s
                WHERE pci.id = %s AND pc.user_id = %s
                """,
                (1 if is_packed else 0, item_id, user_id)
            )
        db.commit()

    @staticmethod
    def delete_checklist_item(user_id, item_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                DELETE pci FROM packing_checklist_items pci
                JOIN packing_checklists pc ON pci.checklist_id = pc.id
                WHERE pci.id = %s AND pc.user_id = %s
                """,
                (item_id, user_id)
            )
        db.commit()

    @staticmethod
    def save_cost_plan(user_id, plan_name, destination_id, hotel_tier, guide_tier, transport_option, group_size, duration_days):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM destinations WHERE id = %s", (destination_id,))
            dest = cursor.fetchone()
            if not dest:
                raise ValueError("Destination not found")
                
            package_cost = float(dest["price_per_person"])
            
            hotel_cost_per_night = {
                "budget": 1000.00,
                "standard": 3000.00,
                "premium": 8000.00
            }.get(hotel_tier.lower(), float(dest["hotel_price_per_night"]))
            
            guide_cost_per_day = {
                "local": 3000.00,
                "licensed": 6000.00
            }.get(guide_tier.lower(), float(dest["guide_fee_per_day"]))
            
            transportation_cost = {
                "local_bus": 1000.00,
                "tourist_bus": 2500.00,
                "private_jeep": 15000.00,
                "flight": 12000.00
            }.get(transport_option.lower(), float(dest["transportation_fee"]))
            
            cursor.execute(
                """
                SELECT COALESCE(SUM(p.cost_npr), 0.00) AS total_permits
                FROM destination_permits dp
                JOIN permits p ON dp.permit_id = p.id
                WHERE dp.destination_id = %s
                """,
                (destination_id,)
            )
            permit_costs_total = float(cursor.fetchone()["total_permits"])
            if permit_costs_total == 0.00:
                permit_costs_total = float(dest["permit_fee"])
                
            nights = max(1, int(duration_days) - 1)
            days = int(duration_days)
            
            trek_package_cost = package_cost * int(group_size)
            hotel_cost = hotel_cost_per_night * nights * int(group_size)
            guide_cost = guide_cost_per_day * days
            permit_costs = permit_costs_total * int(group_size)
            
            if int(group_size) == 1:
                group_size_adjustment = 0.10 * trek_package_cost
            elif int(group_size) >= 6:
                group_size_adjustment = -0.10 * trek_package_cost
            elif int(group_size) >= 3:
                group_size_adjustment = -0.05 * trek_package_cost
            else:
                group_size_adjustment = 0.00
                
            final_total_cost = (trek_package_cost + hotel_cost + guide_cost + transportation_cost + permit_costs + group_size_adjustment)
            
            cursor.execute(
                """
                INSERT INTO cost_breakdown_records (
                    user_id, destination_id, trek_package_cost, hotel_cost_per_night,
                    number_of_nights, guide_cost_per_day, number_of_days, transportation_cost,
                    permit_costs, group_size_adjustment, final_total_cost
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id, destination_id, trek_package_cost, hotel_cost_per_night,
                    nights, guide_cost_per_day, days, transportation_cost,
                    permit_costs, group_size_adjustment, final_total_cost
                )
            )
            plan_id = cursor.lastrowid
        db.commit()
        return plan_id

    @staticmethod
    def get_user_plans(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT c.*, d.name AS dest_name
                FROM cost_breakdown_records c
                JOIN destinations d ON c.destination_id = d.id
                WHERE c.user_id = %s AND c.booking_id IS NULL
                ORDER BY c.created_at DESC
                """,
                (user_id,)
            )
            return cursor.fetchall()

    @staticmethod
    def delete_cost_plan(user_id, plan_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "DELETE FROM cost_breakdown_records WHERE id = %s AND user_id = %s AND booking_id IS NULL",
                (plan_id, user_id)
            )
        db.commit()

    @staticmethod
    def generate_trek_recommendations(user_id):
        db = get_db()
        cursor_dest = db.cursor()
        cursor_dest.execute("SELECT d.*, COALESCE(ts.total_bookings, 0) AS popularity FROM destinations d LEFT JOIN trek_statistics ts ON d.id = ts.destination_id")
        destinations = cursor_dest.fetchall()
        cursor_dest.close()

        with db.cursor() as cursor:
            cursor.execute("SELECT destination_id, difficulty, duration_days FROM bookings WHERE user_id = %s AND booking_status <> 'Cancelled'", (user_id,))
            bookings = cursor.fetchall()
            
            booked_dest_ids = {b["destination_id"] for b in bookings}
            
            diff_counts = {}
            total_durations = 0
            for b in bookings:
                diff_counts[b["difficulty"]] = diff_counts.get(b["difficulty"], 0) + 1
                total_durations += b["duration_days"]
                
            fav_difficulty = max(diff_counts, key=diff_counts.get) if diff_counts else None
            avg_duration = (total_durations / len(bookings)) if bookings else 0
            
            similar_bookings = []
            if booked_dest_ids:
                placeholders = ",".join(["%s"] * len(booked_dest_ids))
                cursor.execute(
                    f"""
                    SELECT DISTINCT b.destination_id
                    FROM bookings b
                    WHERE b.user_id IN (
                        SELECT DISTINCT user_id FROM bookings
                        WHERE destination_id IN ({placeholders}) AND user_id <> %s
                    )
                    """,
                    list(booked_dest_ids) + [user_id]
                )
                similar_bookings = {row["destination_id"] for row in cursor.fetchall()}
                
            import datetime
            current_month = datetime.datetime.now().month
            
            for dest in destinations:
                dest_id = dest["id"]
                score = 50.0
                reasons = []
                
                season_str = dest.get("season", "").lower()
                is_suitable = False
                if current_month in [3, 4, 5] and ("spring" in season_str or "mar-may" in season_str):
                    is_suitable = True
                elif current_month in [9, 10, 11] and ("autumn" in season_str or "sep-nov" in season_str):
                    is_suitable = True
                elif current_month in [5, 6, 7, 8, 9, 10] and "may-oct" in season_str:
                    is_suitable = True
                    
                if is_suitable:
                    score += 20.0
                    reasons.append("Perfect season for this trek")
                    
                if fav_difficulty and dest["difficulty"] == fav_difficulty:
                    score += 15.0
                    reasons.append(f"Matches preferred difficulty ({fav_difficulty})")
                    
                if avg_duration > 0 and abs(dest["duration_days"] - avg_duration) <= 2:
                    score += 15.0
                    reasons.append("Matches preferred trek duration")
                    
                pop = int(dest.get("popularity", 0))
                if pop > 0:
                    bonus = min(15.0, pop * 3.0)
                    score += bonus
                    reasons.append("Popular choice among trekkers")
                    
                if dest_id in similar_bookings:
                    score += 15.0
                    reasons.append("Recommended by similar trekkers")
                    
                if dest_id in booked_dest_ids:
                    score -= 30.0
                    reasons.append("You booked this trek before")
                    
                score = max(0.0, min(100.0, score))
                reason_text = ", ".join(reasons) if reasons else "Selected for you"
                
                cursor.execute(
                    """
                    INSERT INTO trek_recommendations (user_id, destination_id, score, reason)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE score = VALUES(score), reason = VALUES(reason)
                    """,
                    (user_id, dest_id, score, reason_text)
                )
            db.commit()
            
            cursor.execute(
                """
                SELECT r.score, r.reason, d.id, d.name, d.image_url, d.difficulty, d.duration_days, d.price_per_person, d.description, d.altitude_meters
                FROM trek_recommendations r
                JOIN destinations d ON r.destination_id = d.id
                WHERE r.user_id = %s
                ORDER BY r.score DESC LIMIT 6
                """,
                (user_id,)
            )
            return cursor.fetchall()
