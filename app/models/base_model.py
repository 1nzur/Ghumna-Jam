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
    def get_badges():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, slug, name, description, icon, color, requirement_text
                FROM badges
                ORDER BY id
                """
            )
            return cursor.fetchall()

    @staticmethod
    def get_user_badges(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT b.id, b.slug, b.name, b.description, b.icon, b.color, b.requirement_text, ub.earned_at
                FROM badges b
                JOIN user_badges ub ON ub.badge_id = b.id
                WHERE ub.user_id = %s
                ORDER BY ub.earned_at DESC
                """,
                (user_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def add_notification(user_id, message, notification_type="info"):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO user_notifications (user_id, message, type)
                VALUES (%s, %s, %s)
                """,
                (user_id, message, notification_type),
            )
        db.commit()

    @staticmethod
    def get_user_notifications(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, user_id, message, type, is_read, created_at
                FROM user_notifications
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def mark_notifications_read(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE user_notifications
                SET is_read = 1
                WHERE user_id = %s AND is_read = 0
                """,
                (user_id,),
            )
        db.commit()

    @staticmethod
    def award_badge_if_needed(user_id, badge_slug, badge_name, message):
        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id
                    FROM badges
                    WHERE slug = %s
                    """,
                    (badge_slug,),
                )
                badge = cursor.fetchone()
                if badge is None:
                    return False

                cursor.execute(
                    """
                    SELECT 1
                    FROM user_badges
                    WHERE user_id = %s AND badge_id = %s
                    """,
                    (user_id, badge["id"]),
                )
                already_earned = cursor.fetchone() is not None
                if already_earned:
                    return False

                cursor.execute(
                    """
                    INSERT INTO user_badges (user_id, badge_id)
                    VALUES (%s, %s)
                    """,
                    (user_id, badge["id"]),
                )
                cursor.execute(
                    """
                    INSERT INTO user_notifications (user_id, message, type)
                    VALUES (%s, %s, %s)
                    """,
                    (user_id, message, "badge"),
                )
            db.commit()
            return True
        except Exception:
            db.rollback()
            raise
