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
                "role": "ALTER TABLE users ADD COLUMN role VARCHAR(30) NOT NULL DEFAULT 'user'",
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
                    group_type VARCHAR(50),
                    package_name VARCHAR(80),
                    hotel_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    transportation_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    guide_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    permit_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    taxes DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    booking_status VARCHAR(50) NOT NULL DEFAULT 'Confirmed',
                    total_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
            cursor.execute("SHOW COLUMNS FROM bookings")
            booking_columns = {column["Field"] for column in cursor.fetchall()}
            booking_column_statements = {
                "group_type": "ALTER TABLE bookings ADD COLUMN group_type VARCHAR(50)",
                "package_name": "ALTER TABLE bookings ADD COLUMN package_name VARCHAR(80)",
                "hotel_fee": "ALTER TABLE bookings ADD COLUMN hotel_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00",
                "transportation_fee": "ALTER TABLE bookings ADD COLUMN transportation_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00",
                "guide_fee": "ALTER TABLE bookings ADD COLUMN guide_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00",
                "permit_fee": "ALTER TABLE bookings ADD COLUMN permit_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00",
                "taxes": "ALTER TABLE bookings ADD COLUMN taxes DECIMAL(10,2) NOT NULL DEFAULT 0.00",
            }
            for column_name, statement in booking_column_statements.items():
                if column_name not in booking_columns:
                    cursor.execute(statement)

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS destinations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    region VARCHAR(120),
                    image_url VARCHAR(500),
                    difficulty VARCHAR(100),
                    duration_days INT,
                    distance_km DECIMAL(8,2),
                    season VARCHAR(100),
                    description TEXT,
                    price_per_person DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    hotel_price_per_night DECIMAL(10,2) NOT NULL DEFAULT 2500.00,
                    transportation_fee DECIMAL(10,2) NOT NULL DEFAULT 15000.00,
                    guide_fee_per_day DECIMAL(10,2) NOT NULL DEFAULT 3500.00,
                    permit_fee DECIMAL(10,2) NOT NULL DEFAULT 5000.00,
                    altitude_meters INT,
                    highlights TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute("SHOW COLUMNS FROM destinations")
            destination_columns = {column["Field"] for column in cursor.fetchall()}
            destination_column_statements = {
                "region": "ALTER TABLE destinations ADD COLUMN region VARCHAR(120)",
                "distance_km": "ALTER TABLE destinations ADD COLUMN distance_km DECIMAL(8,2)",
                "hotel_price_per_night": "ALTER TABLE destinations ADD COLUMN hotel_price_per_night DECIMAL(10,2) NOT NULL DEFAULT 2500.00",
                "transportation_fee": "ALTER TABLE destinations ADD COLUMN transportation_fee DECIMAL(10,2) NOT NULL DEFAULT 15000.00",
                "guide_fee_per_day": "ALTER TABLE destinations ADD COLUMN guide_fee_per_day DECIMAL(10,2) NOT NULL DEFAULT 3500.00",
                "permit_fee": "ALTER TABLE destinations ADD COLUMN permit_fee DECIMAL(10,2) NOT NULL DEFAULT 5000.00",
            }
            for column_name, statement in destination_column_statements.items():
                if column_name not in destination_columns:
                    cursor.execute(statement)

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
                            185000.00,
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
                            145000.00,
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
                            78000.00,
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
                            165000.00,
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
                            220000.00,
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
                            158000.00,
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
                            260000.00,
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
                            52000.00,
                            4500,
                            "Machapuchare views, forest trails, quiet teahouses",
                        ),
                    ],
                )
            cursor.execute(
                """
                UPDATE destinations
                SET price_per_person = CASE name
                    WHEN 'Everest Base Camp' THEN 185000.00
                    WHEN 'Annapurna Circuit' THEN 145000.00
                    WHEN 'Langtang Valley' THEN 78000.00
                    WHEN 'Manaslu Circuit' THEN 165000.00
                    WHEN 'Upper Mustang' THEN 220000.00
                    WHEN 'Gokyo Lakes & Ri' THEN 158000.00
                    WHEN 'Kanchenjunga Base Camp' THEN 260000.00
                    WHEN 'Mardi Himal' THEN 52000.00
                    ELSE price_per_person
                END
                WHERE price_per_person < 10000
                """
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
                    status VARCHAR(30) NOT NULL DEFAULT 'Published',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
                )
                """
            )
            cursor.execute("SHOW COLUMNS FROM reviews")
            review_columns = {column["Field"] for column in cursor.fetchall()}
            if "status" not in review_columns:
                cursor.execute("ALTER TABLE reviews ADD COLUMN status VARCHAR(30) NOT NULL DEFAULT 'Published'")

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS trails (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    log_data TEXT,
                    distance_km DECIMAL(8,3) NOT NULL DEFAULT 0.000,
                    duration_seconds INT NOT NULL DEFAULT 0,
                    elevation_gain_m DECIMAL(8,2) NOT NULL DEFAULT 0.00,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
            cursor.execute("SHOW COLUMNS FROM trails")
            trail_columns = {column["Field"] for column in cursor.fetchall()}
            trail_column_statements = {
                "distance_km": "ALTER TABLE trails ADD COLUMN distance_km DECIMAL(8,3) NOT NULL DEFAULT 0.000",
                "duration_seconds": "ALTER TABLE trails ADD COLUMN duration_seconds INT NOT NULL DEFAULT 0",
                "elevation_gain_m": "ALTER TABLE trails ADD COLUMN elevation_gain_m DECIMAL(8,2) NOT NULL DEFAULT 0.00",
            }
            for column_name, statement in trail_column_statements.items():
                if column_name not in trail_columns:
                    cursor.execute(statement)

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS emergency_alerts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    latitude DECIMAL(10,7),
                    longitude DECIMAL(10,7),
                    accuracy_m DECIMAL(8,2),
                    message TEXT,
                    status VARCHAR(30) NOT NULL DEFAULT 'Open',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_emergency_status_created (status, created_at)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS checklist_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    item_name VARCHAR(255) NOT NULL,
                    category VARCHAR(80) NOT NULL DEFAULT 'Gear',
                    is_packed TINYINT(1) NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_checklist_user (user_id)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS trek_photos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    destination_id INT,
                    file_path VARCHAR(500) NOT NULL,
                    caption VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE SET NULL,
                    INDEX idx_photos_user (user_id),
                    INDEX idx_photos_destination (destination_id)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS review_replies (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    review_id INT NOT NULL,
                    user_id INT NOT NULL,
                    body TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_replies_review (review_id)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS follows (
                    follower_id INT NOT NULL,
                    following_id INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (follower_id, following_id),
                    FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (following_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS achievements (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    slug VARCHAR(80) NOT NULL UNIQUE,
                    name VARCHAR(120) NOT NULL,
                    description TEXT NOT NULL,
                    threshold_type VARCHAR(40) NOT NULL,
                    threshold_value INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_achievements (
                    user_id INT NOT NULL,
                    achievement_id INT NOT NULL,
                    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, achievement_id),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
                )
                """
            )

            cursor.executemany(
                """
                INSERT IGNORE INTO achievements (slug, name, description, threshold_type, threshold_value)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [
                    ('reached-3000m', 'Reached 3000m', 'Reach an altitude of 3,000m during a trek.', 'altitude', 3000),
                    ('reached-5000m', 'Reached 5000m', 'Reach an altitude of 5,000m during a trek.', 'altitude', 5000),
                    ('reached-7000m', 'Reached 7000m', 'Reach an altitude of 7,000m during a trek.', 'altitude', 7000),
                    ('travelled-50km', 'Travelled 50km', 'Travel a cumulative distance of 50km.', 'distance', 50),
                    ('travelled-100km', 'Travelled 100km', 'Travel a cumulative distance of 100km.', 'distance', 100),
                    ('travelled-500km', 'Travelled 500km', 'Travel a cumulative distance of 500km.', 'distance', 500),
                    ('first-trek', 'First Trek', 'Book and complete your first Himalayan trek.', 'bookings', 1),
                    ('five-treks', '5 Treks Completed', 'Complete 5 different trek departures.', 'bookings', 5),
                    ('ten-treks', '10 Treks Completed', 'Complete 10 different trek departures.', 'bookings', 10),
                    ('twenty-five-treks', '25 Treks Completed', 'Complete 25 different trek departures.', 'bookings', 25),
                    ('first-review', 'First Review', 'Share your experience by writing your first review.', 'reviews', 1),
                    ('first-photo', 'First Photo Upload', 'Upload your first trek photo to the gallery.', 'photos', 1),
                    ('first-follower', 'First Follower', 'Get your first follower in the community.', 'followers', 1),
                    ('ten-followers', '10 Followers', 'Build your audience and reach 10 followers.', 'followers', 10),
                    ('fifty-followers', '50 Followers', 'Become a popular guide/trekker with 50 followers.', 'followers', 50)
                ],
            )

            # Create Permits & Destination Permits tables
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS permits (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    cost_npr DECIMAL(10,2) NOT NULL DEFAULT 0.00
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS destination_permits (
                    destination_id INT NOT NULL,
                    permit_id INT NOT NULL,
                    PRIMARY KEY (destination_id, permit_id),
                    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE,
                    FOREIGN KEY (permit_id) REFERENCES permits(id) ON DELETE CASCADE
                )
                """
            )

            # Create Trip History
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS trip_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    booking_id INT NOT NULL,
                    destination_id INT NOT NULL,
                    history_status VARCHAR(50) NOT NULL DEFAULT 'Upcoming',
                    start_date DATE,
                    end_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
                    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
                )
                """
            )

            # Create Trek Tracking Sessions
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS trek_tracking_sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    trip_id INT,
                    title VARCHAR(255) NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP NULL,
                    total_distance_km DECIMAL(8,3) DEFAULT 0.000,
                    total_duration_seconds INT DEFAULT 0,
                    elevation_gain_meters DECIMAL(8,2) DEFAULT 0.00,
                    avg_speed_kmh DECIMAL(5,2) DEFAULT 0.00,
                    max_altitude_meters INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (trip_id) REFERENCES trip_history(id) ON DELETE SET NULL
                )
                """
            )

            # Create GPS Route Points
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS gps_route_points (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id INT NOT NULL,
                    latitude DECIMAL(10,7) NOT NULL,
                    longitude DECIMAL(10,7) NOT NULL,
                    altitude DECIMAL(8,2) DEFAULT 0.00,
                    distance_travelled_km DECIMAL(8,3) DEFAULT 0.000,
                    elapsed_seconds INT DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES trek_tracking_sessions(id) ON DELETE CASCADE
                )
                """
            )

            # Create Elevation History
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS elevation_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id INT NOT NULL,
                    altitude DECIMAL(8,2) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES trek_tracking_sessions(id) ON DELETE CASCADE
                )
                """
            )

            # Create Packing Checklists
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS packing_checklists (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )

            # Create Packing Checklist Items
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS packing_checklist_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    checklist_id INT NOT NULL,
                    item_name VARCHAR(255) NOT NULL,
                    category VARCHAR(80) NOT NULL DEFAULT 'Gear',
                    is_packed TINYINT(1) NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (checklist_id) REFERENCES packing_checklists(id) ON DELETE CASCADE
                )
                """
            )

            # Create Trek Recommendations
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS trek_recommendations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    destination_id INT NOT NULL,
                    score DECIMAL(5,2) NOT NULL DEFAULT 0.00,
                    reason VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_user_recommendation (user_id, destination_id)
                )
                """
            )

            # Create Review Photos
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS review_photos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    review_id INT NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
                )
                """
            )

            # Create User Statistics
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_statistics (
                    user_id INT PRIMARY KEY,
                    total_distance_km DECIMAL(10,2) DEFAULT 0.00,
                    total_duration_hours DECIMAL(10,2) DEFAULT 0.00,
                    completed_treks_count INT DEFAULT 0,
                    max_altitude_reached INT DEFAULT 0,
                    reviews_count INT DEFAULT 0,
                    photos_uploaded_count INT DEFAULT 0,
                    followers_count INT DEFAULT 0,
                    following_count INT DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )

            # Create Trek Statistics
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS trek_statistics (
                    destination_id INT PRIMARY KEY,
                    total_bookings INT DEFAULT 0,
                    average_rating DECIMAL(3,2) DEFAULT 0.00,
                    reviews_count INT DEFAULT 0,
                    photos_count INT DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
                )
                """
            )

            # Create Cost Breakdown Records
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS cost_breakdown_records (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    booking_id INT,
                    user_id INT NOT NULL,
                    destination_id INT NOT NULL,
                    trek_package_cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    hotel_cost_per_night DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    number_of_nights INT NOT NULL DEFAULT 0,
                    guide_cost_per_day DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    number_of_days INT NOT NULL DEFAULT 0,
                    transportation_cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    permit_costs DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    group_size_adjustment DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    final_total_cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE,
                    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE SET NULL
                )
                """
            )

            # Seed permits
            cursor.executemany(
                """
                INSERT IGNORE INTO permits (name, cost_npr) VALUES (%s, %s)
                """,
                [
                    ('TIMS Card', 2000.00),
                    ('ACAP Permit', 3000.00),
                    ('Sagarmatha Permit', 3000.00),
                    ('Langtang Permit', 3000.00),
                    ('Manaslu Permit', 10000.00),
                    ('Upper Mustang Permit', 70000.00)
                ]
            )

            # Seed destination permits mapping
            cursor.execute("SELECT id, name FROM destinations")
            d_map = {row["name"]: row["id"] for row in cursor.fetchall()}
            cursor.execute("SELECT id, name FROM permits")
            p_map = {row["name"]: row["id"] for row in cursor.fetchall()}

            dp_seeds = []
            tims_id = p_map.get("TIMS Card")
            if tims_id:
                for dest_name, dest_id in d_map.items():
                    dp_seeds.append((dest_id, tims_id))

            acap_id = p_map.get("ACAP Permit")
            if acap_id:
                for name in ["Annapurna Circuit", "Mardi Himal", "Manaslu Circuit", "Upper Mustang"]:
                    if name in d_map:
                        dp_seeds.append((d_map[name], acap_id))

            sag_id = p_map.get("Sagarmatha Permit")
            if sag_id:
                for name in ["Everest Base Camp", "Gokyo Lakes & Ri", "Kanchenjunga Base Camp"]:
                    if name in d_map:
                        dp_seeds.append((d_map[name], sag_id))

            lang_id = p_map.get("Langtang Permit")
            if lang_id:
                if "Langtang Valley" in d_map:
                    dp_seeds.append((d_map["Langtang Valley"], lang_id))

            manaslu_id = p_map.get("Manaslu Permit")
            if manaslu_id:
                if "Manaslu Circuit" in d_map:
                    dp_seeds.append((d_map["Manaslu Circuit"], manaslu_id))

            mustang_id = p_map.get("Upper Mustang Permit")
            if mustang_id:
                if "Upper Mustang" in d_map:
                    dp_seeds.append((d_map["Upper Mustang"], mustang_id))

            cursor.executemany(
                "INSERT IGNORE INTO destination_permits (destination_id, permit_id) VALUES (%s, %s)",
                dp_seeds
            )

            # Update destinations with realistic pricing
            cursor.execute(
                """
                UPDATE destinations
                SET price_per_person = CASE name
                    WHEN 'Everest Base Camp' THEN 65000.00
                    WHEN 'Annapurna Circuit' THEN 55000.00
                    WHEN 'Langtang Valley' THEN 35000.00
                    WHEN 'Manaslu Circuit' THEN 85000.00
                    WHEN 'Upper Mustang' THEN 145000.00
                    WHEN 'Gokyo Lakes & Ri' THEN 58000.00
                    WHEN 'Kanchenjunga Base Camp' THEN 160000.00
                    WHEN 'Mardi Himal' THEN 25000.00
                    ELSE price_per_person
                END,
                hotel_price_per_night = CASE name
                    WHEN 'Everest Base Camp' THEN 2500.00
                    WHEN 'Annapurna Circuit' THEN 1800.00
                    WHEN 'Langtang Valley' THEN 1200.00
                    WHEN 'Manaslu Circuit' THEN 1500.00
                    WHEN 'Upper Mustang' THEN 3000.00
                    WHEN 'Gokyo Lakes & Ri' THEN 2200.00
                    WHEN 'Kanchenjunga Base Camp' THEN 1800.00
                    WHEN 'Mardi Himal' THEN 1000.00
                    ELSE hotel_price_per_night
                END,
                transportation_fee = CASE name
                    WHEN 'Everest Base Camp' THEN 18000.00
                    WHEN 'Annapurna Circuit' THEN 4500.00
                    WHEN 'Langtang Valley' THEN 2500.00
                    WHEN 'Manaslu Circuit' THEN 12000.00
                    WHEN 'Upper Mustang' THEN 22000.00
                    WHEN 'Gokyo Lakes & Ri' THEN 18000.00
                    WHEN 'Kanchenjunga Base Camp' THEN 24000.00
                    WHEN 'Mardi Himal' THEN 2000.00
                    ELSE transportation_fee
                END,
                guide_fee_per_day = CASE name
                    WHEN 'Everest Base Camp' THEN 5000.00
                    WHEN 'Annapurna Circuit' THEN 4500.00
                    WHEN 'Langtang Valley' THEN 3500.00
                    WHEN 'Manaslu Circuit' THEN 5000.00
                    WHEN 'Upper Mustang' THEN 6000.00
                    WHEN 'Gokyo Lakes & Ri' THEN 4500.00
                    WHEN 'Kanchenjunga Base Camp' THEN 5500.00
                    WHEN 'Mardi Himal' THEN 3500.00
                    ELSE guide_fee_per_day
                END,
                permit_fee = CASE name
                    WHEN 'Everest Base Camp' THEN 5000.00
                    WHEN 'Annapurna Circuit' THEN 5000.00
                    WHEN 'Langtang Valley' THEN 5000.00
                    WHEN 'Manaslu Circuit' THEN 15000.00
                    WHEN 'Upper Mustang' THEN 75000.00
                    WHEN 'Gokyo Lakes & Ri' THEN 5000.00
                    WHEN 'Kanchenjunga Base Camp' THEN 5000.00
                    WHEN 'Mardi Himal' THEN 5000.00
                    ELSE permit_fee
                END
                """
            )
        db.commit()
