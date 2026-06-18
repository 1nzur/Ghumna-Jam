import pymysql
from werkzeug.security import check_password_hash, generate_password_hash

from app.models.database import get_db


class BaseModel:
    @staticmethod
    def get_user_by_email(email):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, full_name, email, password_hash, phone_number, date_of_birth, profile_picture_url
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
                SELECT id, full_name, email, password_hash, phone_number, date_of_birth, profile_picture_url
                FROM users
                WHERE id = %s
                """,
                (user_id,),
            )
            return cursor.fetchone()

    @staticmethod
    def update_user(
        user_id,
        full_name,
        email,
        phone_number=None,
        date_of_birth=None,
        profile_picture_url=None,
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
                            password_hash = %s
                        WHERE id = %s
                        """,
                        (
                            full_name,
                            email,
                            phone_number,
                            date_of_birth or None,
                            profile_picture_url,
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
                            profile_picture_url = %s
                        WHERE id = %s
                        """,
                        (
                            full_name,
                            email,
                            phone_number,
                            date_of_birth or None,
                            profile_picture_url,
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
    def record_trek(user_id, distance_km, duration_seconds, points_json=None):
        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO trek_records (user_id, distance_km, duration_seconds, points_json)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, distance_km, duration_seconds, points_json),
                )
            db.commit()
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_last_trek(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT distance_km, duration_seconds, completed_at
                FROM trek_records
                WHERE user_id = %s
                ORDER BY completed_at DESC
                LIMIT 1
                """,
                (user_id,),
            )
            return cursor.fetchone()

    @staticmethod
    def get_total_distance(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT SUM(distance_km) as total_distance
                FROM trek_records
                WHERE user_id = %s
                """,
                (user_id,),
            )
            result = cursor.fetchone()
            return result["total_distance"] if result and result["total_distance"] else 0.0

    @staticmethod
    def get_all_users(exclude_user_id=None):
        db = get_db()
        with db.cursor() as cursor:
            query = """
                SELECT id, full_name, email, profile_picture_url
                FROM users
            """
            params = []
            if exclude_user_id is not None:
                query += " WHERE id != %s"
                params.append(exclude_user_id)
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def get_followers(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT u.id, u.full_name, u.profile_picture_url
                FROM users u
                JOIN follows f ON u.id = f.follower_id
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
                SELECT u.id, u.full_name, u.profile_picture_url
                FROM users u
                JOIN follows f ON u.id = f.following_id
                WHERE f.follower_id = %s
                ORDER BY u.full_name
                """,
                (user_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def follow_user(follower_id, following_id):
        if follower_id == following_id:
            return

        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    "INSERT IGNORE INTO follows (follower_id, following_id) VALUES (%s, %s)",
                    (follower_id, following_id),
                )
            db.commit()
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def unfollow_user(follower_id, following_id):
        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM follows WHERE follower_id = %s AND following_id = %s",
                    (follower_id, following_id),
                )
            db.commit()
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_notifications(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT n.id, n.actor_id, n.message, n.is_read, n.created_at,
                       u.full_name AS actor_name, u.profile_picture_url AS actor_profile_picture_url
                FROM notifications n
                LEFT JOIN users u ON u.id = n.actor_id
                WHERE n.user_id = %s
                ORDER BY n.created_at DESC
                """,
                (user_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def notify_followers(actor_id, message):
        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT follower_id FROM follows WHERE following_id = %s",
                    (actor_id,),
                )
                follower_rows = cursor.fetchall()
                if not follower_rows:
                    return
                for row in follower_rows:
                    cursor.execute(
                        "INSERT INTO notifications (user_id, actor_id, message) VALUES (%s, %s, %s)",
                        (row["follower_id"], actor_id, message),
                    )
            db.commit()
        except Exception:
            db.rollback()
            raise
