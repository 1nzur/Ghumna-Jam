import pymysql
import config
from flask import current_app, g


class Database:
    def __init__(self):
        """Open a database connection when object is created."""
        try:
            self.__connection = pymysql.connect(
                host=config.MYSQL_HOST,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD,
                database=config.MYSQL_DATABASE,
                cursorclass=pymysql.cursors.DictCursor,
            )
            print("Database connected successfully!")
        except pymysql.MySQLError as e:
            self.__connection = None
            print("Database connection failed!")
            print("Error:", e)

    @property
    def connection(self):
        return self.__connection

    def close(self):
        if self.__connection is not None:
            self.__connection.close()


def get_db():
    if "db" not in g:
        g.db = pymysql.connect(
            host=current_app.config["MYSQL_HOST"],
            user=current_app.config["MYSQL_USER"],
            password=current_app.config["MYSQL_PASSWORD"],
            database=current_app.config["MYSQL_DATABASE"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    with app.app_context():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(120) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    phone_number VARCHAR(30),
                    date_of_birth DATE,
                    profile_picture_url VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute("SHOW COLUMNS FROM users")
            existing_columns = {column["Field"] for column in cursor.fetchall()}
            profile_columns = {
                "phone_number": "ALTER TABLE users ADD COLUMN phone_number VARCHAR(30)",
                "date_of_birth": "ALTER TABLE users ADD COLUMN date_of_birth DATE",
                "profile_picture_url": "ALTER TABLE users ADD COLUMN profile_picture_url VARCHAR(500)",
            }

            for column_name, statement in profile_columns.items():
                if column_name not in existing_columns:
                    cursor.execute(statement)
        db.commit()
