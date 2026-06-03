import pymysql
from werkzeug.security import check_password_hash, generate_password_hash

from app.models.database import get_db


class BaseModel:
    PASSWORD_HASH_METHOD = "pbkdf2:sha256"

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
                            generate_password_hash(
                                password,
                                method=BaseModel.PASSWORD_HASH_METHOD,
                            ),
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
        password_hash = generate_password_hash(
            password,
            method=BaseModel.PASSWORD_HASH_METHOD,
        )

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
