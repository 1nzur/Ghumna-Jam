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
                    emergency_contact_name VARCHAR(255),
                    emergency_contact_phone VARCHAR(30),
                    reset_token VARCHAR(255),
                    reset_token_expires DATETIME,
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
                "emergency_contact_name": "ALTER TABLE users ADD COLUMN emergency_contact_name VARCHAR(255)",
                "emergency_contact_phone": "ALTER TABLE users ADD COLUMN emergency_contact_phone VARCHAR(30)",
                "reset_token": "ALTER TABLE users ADD COLUMN reset_token VARCHAR(255)",
                "reset_token_expires": "ALTER TABLE users ADD COLUMN reset_token_expires DATETIME",
            }

            for column_name, statement in profile_columns.items():
                if column_name not in existing_columns:
                    cursor.execute(statement)

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS bookings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    destination_id INT NOT NULL,
                    destination_name VARCHAR(255) NOT NULL,
                    destination_image_url VARCHAR(500),
                    departure_date DATE,
                    travelers_count INT NOT NULL DEFAULT 1,
                    duration_days INT,
                    difficulty VARCHAR(100),
                    selected_hotel VARCHAR(255),
                    booking_status VARCHAR(50) NOT NULL DEFAULT 'Confirmed',
                    total_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS destinations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    image_url VARCHAR(500),
                    difficulty VARCHAR(100),
                    duration_days INT,
                    season VARCHAR(100),
                    description TEXT,
                    price_per_person DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    altitude_meters INT,
                    highlights TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute("SELECT COUNT(*) AS count FROM destinations")
            destination_count = cursor.fetchone().get("count", 0)
            if destination_count == 0:
                cursor.executemany(
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
                    [
                        (
                            "Everest Base Camp",
                            "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
                            "Moderate",
                            14,
                            "Mar-May, Sep-Nov",
                            "A classic Himalayan trek through Sherpa villages, alpine valleys, and dramatic views of the world's highest peaks.",
                            1499.00,
                            5364,
                            "Sherpa culture, Kala Patthar viewpoint, historic base camp",
                        ),
                        (
                            "Annapurna Circuit",
                            "https://images.unsplash.com/photo-1517021897933-0e0319cfbc28?auto=format&fit=crop&w=1200&q=80",
                            "Challenging",
                            12,
                            "Oct-Nov",
                            "A sweeping circuit through river valleys, high passes, and traditional mountain settlements.",
                            1199.00,
                            5416,
                            "Thorong La Pass, Kali Gandaki Gorge, diverse landscapes",
                        ),
                        (
                            "Langtang Valley",
                            "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
                            "Moderate",
                            8,
                            "Mar-May",
                            "A beautiful alpine route with glacier views, yak pastures, and rich Tamang culture.",
                            799.00,
                            3870,
                            "Kyanjin Gompa, Yak pastures, panoramic glaciers",
                        ),
                        (
                            "Manaslu Circuit",
                            "https://images.unsplash.com/photo-1605649487212-47bdab064df7?auto=format&fit=crop&w=1200&q=80",
                            "Challenging",
                            14,
                            "Oct-Nov",
                            "A remote, spectacular loop around the world's eighth-highest mountain, featuring the challenging Larkya La Pass.",
                            1399.00,
                            5106,
                            "Larkya La Pass, Buddhist monasteries, border region cultures",
                        ),
                        (
                            "Upper Mustang",
                            "https://images.unsplash.com/photo-1548565431-7e8c312521f7?auto=format&fit=crop&w=1200&q=80",
                            "Moderate",
                            10,
                            "May-Oct",
                            "Explore the ancient, dry kingdom of Lo Manthang, characterized by red cliffs, cave dwellings, and Tibetan culture.",
                            1799.00,
                            3840,
                            "Lo Manthang walled city, sky caves, Tibetan-style palace",
                        ),
                        (
                            "Gokyo Lakes & Ri",
                            "https://images.unsplash.com/photo-1589308078059-be1415eab4c3?auto=format&fit=crop&w=1200&q=80",
                            "Moderate",
                            12,
                            "Mar-May, Sep-Nov",
                            "Trek to the turquoise glacial lakes of the Gokyo Valley and climb Gokyo Ri for premium views of Everest and Lhotse.",
                            1299.00,
                            5357,
                            "Turquoise lakes, Ngozumpa Glacier, views of four 8,000m peaks",
                        ),
                        (
                            "Kanchenjunga Base Camp",
                            "https://images.unsplash.com/photo-1533240332313-0db49b459ad6?auto=format&fit=crop&w=1200&q=80",
                            "Challenging",
                            20,
                            "Oct-Nov, Mar-May",
                            "A long journey to the far eastern border of Nepal to reach the base camp of Kanchenjunga, the world's third highest peak.",
                            2199.00,
                            5143,
                            "Remote wilderness, Limbu culture, views of Yalung glacier",
                        ),
                        (
                            "Mardi Himal",
                            "https://images.unsplash.com/photo-1491555180598-88ee14744f4f?auto=format&fit=crop&w=1200&q=80",
                            "Easy",
                            6,
                            "Mar-May, Sep-Nov",
                            "A short, beautiful trek offering up-close views of Mount Machapuchare (Fishtail) and the Annapurna range.",
                            599.00,
                            4500,
                            "Machapuchare views, forest trails, quiet teahouses",
                        ),
                    ],
                )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS favorite_destinations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    destination_id INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_user_destination (user_id, destination_id),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS reviews (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    destination_id INT NOT NULL,
                    rating TINYINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS trails (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    log_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
        db.commit()
