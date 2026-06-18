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

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS badges (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    slug VARCHAR(80) NOT NULL UNIQUE,
                    name VARCHAR(120) NOT NULL,
                    description TEXT NOT NULL,
                    icon VARCHAR(20) NOT NULL,
                    color VARCHAR(40) NOT NULL,
                    requirement_text VARCHAR(120) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_badges (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    badge_id INT NOT NULL,
                    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uq_user_badge (user_id, badge_id),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_notifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    message VARCHAR(255) NOT NULL,
                    type VARCHAR(40) DEFAULT 'info',
                    is_read TINYINT(1) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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

            cursor.execute(
                """
                INSERT IGNORE INTO badges (slug, name, description, icon, color, requirement_text)
                VALUES
                    ('first-trek', 'First Trek', 'Complete your first trek booking.', '🥾', 'from-amber-500 to-yellow-400', 'Complete 1 trek'),
                    ('summit-scout', 'Summit Scout', 'Finish three memorable treks and earn your explorer stripes.', '🏔️', 'from-sky-500 to-cyan-400', 'Complete 3 treks'),
                    ('trail-master', 'Trail Master', 'Reach the top with five completed adventures.', '👑', 'from-orange-500 to-amber-400', 'Complete 5 treks')
                """
            )
        db.commit()
