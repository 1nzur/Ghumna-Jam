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

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS bookings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    dest_name VARCHAR(255) NOT NULL,
                    dest_image VARCHAR(500),
                    status VARCHAR(50) DEFAULT 'Confirmed',
                    departure_date VARCHAR(50),
                    travelers_count INT DEFAULT 1,
                    duration_days INT,
                    difficulty VARCHAR(50),
                    selected_hotel VARCHAR(255),
                    total_price DECIMAL(12,2),
                    booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )

            # Migrate bookings table to new schema if columns are missing
            cursor.execute("SHOW COLUMNS FROM bookings")
            booking_cols = {col["Field"] for col in cursor.fetchall()}
            booking_migrations = {
                "user_id":         "ALTER TABLE bookings ADD COLUMN user_id INT NOT NULL DEFAULT 0",
                "dest_name":       "ALTER TABLE bookings ADD COLUMN dest_name VARCHAR(255)",
                "dest_image":      "ALTER TABLE bookings ADD COLUMN dest_image VARCHAR(500)",
                "status":          "ALTER TABLE bookings ADD COLUMN status VARCHAR(50) DEFAULT 'Confirmed'",
                "departure_date":  "ALTER TABLE bookings ADD COLUMN departure_date VARCHAR(50)",
                "travelers_count": "ALTER TABLE bookings ADD COLUMN travelers_count INT DEFAULT 1",
                "duration_days":   "ALTER TABLE bookings ADD COLUMN duration_days INT",
                "difficulty":      "ALTER TABLE bookings ADD COLUMN difficulty VARCHAR(50)",
                "selected_hotel":  "ALTER TABLE bookings ADD COLUMN selected_hotel VARCHAR(255)",
                "total_price":     "ALTER TABLE bookings ADD COLUMN total_price DECIMAL(12,2)",
                "booked_at":       "ALTER TABLE bookings ADD COLUMN booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            }
            for col, stmt in booking_migrations.items():
                if col not in booking_cols:
                    cursor.execute(stmt)

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS checklist_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    item_name VARCHAR(255) NOT NULL,
                    category VARCHAR(100) NOT NULL DEFAULT 'General',
                    is_checked TINYINT(1) NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )

            cursor.execute("SHOW COLUMNS FROM checklist_items")
            checklist_columns = {col["Field"] for col in cursor.fetchall()}
            checklist_migrations = {
                "item_name": "ALTER TABLE checklist_items ADD COLUMN item_name VARCHAR(255) NOT NULL DEFAULT ''",
                "category": "ALTER TABLE checklist_items ADD COLUMN category VARCHAR(100) NOT NULL DEFAULT 'General'",
                "is_checked": "ALTER TABLE checklist_items ADD COLUMN is_checked TINYINT(1) NOT NULL DEFAULT 0",
            }
            for col, stmt in checklist_migrations.items():
                if col not in checklist_columns:
                    cursor.execute(stmt)

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS trek_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    dest_name VARCHAR(255) NOT NULL,
                    difficulty VARCHAR(50) NOT NULL DEFAULT 'Moderate',
                    duration_days INT NOT NULL DEFAULT 0,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS destination_reviews (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    dest_id INT NOT NULL,
                    rating INT NOT NULL,
                    comment TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY one_review_per_user (user_id, dest_id),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_badges (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    badge_slug VARCHAR(50) NOT NULL,
                    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uniq_user_badge (user_id, badge_slug),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    message VARCHAR(500) NOT NULL,
                    is_read TINYINT(1) NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )

        # ── Admin tables (separate cursor to avoid stale-result issues) ────────
        with db.cursor() as cur:

            # Add is_admin role column to users if it doesn't exist yet
            cur.execute("SHOW COLUMNS FROM users")
            user_cols = {col["Field"] for col in cur.fetchall()}
            if "is_admin" not in user_cols:
                cur.execute(
                    "ALTER TABLE users ADD COLUMN is_admin TINYINT(1) NOT NULL DEFAULT 0"
                )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS destinations (
                    id               INT AUTO_INCREMENT PRIMARY KEY,
                    name             VARCHAR(255)    NOT NULL,
                    category         VARCHAR(50)     NOT NULL DEFAULT 'hike',
                    image_url        VARCHAR(500),
                    difficulty       VARCHAR(50)     DEFAULT 'Moderate',
                    duration_days    INT             DEFAULT 7,
                    season           VARCHAR(100),
                    description      TEXT,
                    price_per_person DECIMAL(12, 2)  DEFAULT 0,
                    altitude_meters  INT             DEFAULT 0,
                    highlights       TEXT,
                    is_active        TINYINT(1)      NOT NULL DEFAULT 1,
                    created_at       TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
                    updated_at       TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
                                                     ON UPDATE CURRENT_TIMESTAMP
                )
                """
            )

            # Migrate existing destinations table that may be missing new columns
            cur.execute("SHOW COLUMNS FROM destinations")
            dest_cols = {col["Field"] for col in cur.fetchall()}
            dest_migrations = {
                "category":  "ALTER TABLE destinations ADD COLUMN category VARCHAR(50) NOT NULL DEFAULT 'hike'",
                "is_active": "ALTER TABLE destinations ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1",
                "updated_at": "ALTER TABLE destinations ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
            }
            for col, stmt in dest_migrations.items():
                if col not in dest_cols:
                    cur.execute(stmt)

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS announcements (
                    id          INT AUTO_INCREMENT PRIMARY KEY,
                    title       VARCHAR(255)  NOT NULL,
                    message     TEXT          NOT NULL,
                    type        VARCHAR(20)   NOT NULL DEFAULT 'info',
                    is_active   TINYINT(1)   NOT NULL DEFAULT 1,
                    created_by  INT,
                    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS homepage_content (
                    id           INT AUTO_INCREMENT PRIMARY KEY,
                    section_key  VARCHAR(100) NOT NULL UNIQUE,
                    title        VARCHAR(255),
                    subtitle     TEXT,
                    body         TEXT,
                    updated_by   INT,
                    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                           ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS site_photos (
                    id          INT AUTO_INCREMENT PRIMARY KEY,
                    title       VARCHAR(255),
                    image_url   VARCHAR(500)  NOT NULL,
                    section     VARCHAR(100)  NOT NULL DEFAULT 'gallery',
                    is_active   TINYINT(1)   NOT NULL DEFAULT 1,
                    sort_order  INT          NOT NULL DEFAULT 0,
                    uploaded_by INT,
                    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
                )
                """
            )

            # Seed all 16 destinations; INSERT IGNORE skips rows that already exist
            _seed_destinations(cur)

            # Backfill category for rows that existed before the column was added
            _backfill_dest_categories(cur)

        db.commit()


# NPR exchange rate used when seeding prices from the original USD values
_EXCHANGE_RATE = 134.0


def _backfill_dest_categories(cursor):
    """Fix category on rows that were created before the category column existed."""
    category_map = {
        1: "basecamp", 2: "cultural", 3: "cultural", 4: "basecamp",
        5: "cultural", 6: "basecamp", 7: "basecamp", 8: "hike",
        9: "hike", 10: "hike", 11: "hike", 12: "basecamp",
        13: "cultural", 14: "cultural", 15: "basecamp", 16: "basecamp",
    }
    for dest_id, cat in category_map.items():
        cursor.execute(
            "UPDATE destinations SET category=%s WHERE id=%s AND category='hike' AND %s != 'hike'",
            (cat, dest_id, cat),
        )


def _seed_destinations(cursor):
    """Insert all 16 trek routes; skips rows whose id already exists."""
    rows = [
        (1,  "Everest Base Camp",         "basecamp", "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",  "Moderate",    14, "Mar-May, Sep-Nov", "A classic Himalayan trek through Sherpa villages, alpine valleys, and dramatic views of the world's highest peaks.",                                                 round(1299.00 * _EXCHANGE_RATE, 2), 5364, "Sherpa culture, Kala Patthar viewpoint, historic base camp"),
        (2,  "Annapurna Circuit",          "cultural", "https://images.unsplash.com/photo-1517021897933-0e0319cfbc28?auto=format&fit=crop&w=1200&q=80",  "Challenging", 12, "Oct-Nov",          "A sweeping circuit through river valleys, high passes, and traditional mountain settlements.",                                                                          round(999.00  * _EXCHANGE_RATE, 2), 5416, "Thorong La Pass, Kali Gandaki Gorge, diverse landscapes"),
        (3,  "Langtang Valley",            "cultural", "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",  "Moderate",    8,  "Mar-May",          "A beautiful alpine route with glacier views, yak pastures, and rich Tamang culture.",                                                                                   round(649.00  * _EXCHANGE_RATE, 2), 3870, "Kyanjin Gompa, Yak pastures, panoramic glaciers"),
        (4,  "Manaslu Circuit",            "basecamp", "https://images.unsplash.com/photo-1605649487212-47bdab064df7?auto=format&fit=crop&w=1200&q=80",  "Challenging", 14, "Oct-Nov",          "A remote, spectacular loop around the world's eighth-highest mountain, featuring the challenging Larkya La Pass.",                                                     round(1099.00 * _EXCHANGE_RATE, 2), 5106, "Larkya La Pass, Buddhist monasteries, border region cultures"),
        (5,  "Upper Mustang",              "cultural", "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",  "Moderate",    10, "May-Oct",          "Explore the ancient, dry kingdom of Lo Manthang, characterized by red cliffs, cave dwellings, and Tibetan culture.",                                                  round(1899.00 * _EXCHANGE_RATE, 2), 3840, "Lo Manthang walled city, sky caves, Tibetan-style palace"),
        (6,  "Gokyo Lakes & Ri",           "basecamp", "https://images.unsplash.com/photo-1589308078059-be1415eab4c3?auto=format&fit=crop&w=1200&q=80",  "Moderate",    12, "Mar-May, Sep-Nov", "Trek to the turquoise glacial lakes of the Gokyo Valley and climb Gokyo Ri for premium views of Everest and Lhotse.",                                                 round(1249.00 * _EXCHANGE_RATE, 2), 5357, "Turquoise lakes, Ngozumpa Glacier, views of four 8,000m peaks"),
        (7,  "Kanchenjunga Base Camp",     "basecamp", "https://images.unsplash.com/photo-1533240332313-0db49b459ad6?auto=format&fit=crop&w=1200&q=80",  "Challenging", 20, "Oct-Nov, Mar-May", "A long journey to the far eastern border of Nepal to reach the base camp of Kanchenjunga, the world's third highest peak.",                                           round(2199.00 * _EXCHANGE_RATE, 2), 5143, "Remote wilderness, Limbu culture, views of Yalung glacier"),
        (8,  "Mardi Himal",                "hike",     "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80",  "Easy",        6,  "Mar-May, Sep-Nov", "A short, beautiful trek offering up-close views of Mount Machapuchare (Fishtail) and the Annapurna range.",                                                          round(449.00  * _EXCHANGE_RATE, 2), 4500, "Machapuchare views, forest trails, quiet teahouses"),
        (9,  "Poon Hill Trek",             "hike",     "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",  "Easy",        5,  "Sep-May",          "A classic short trek in the Annapurna foothills, famous for its panoramic sunrise views over Dhaulagiri and Annapurna.",                                              round(299.00  * _EXCHANGE_RATE, 2), 3210, "Sunrise over Annapurna, rhododendron forests, Gurung heritage"),
        (10, "Gosaikunda Lake",            "hike",     "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1200&q=80",  "Moderate",    7,  "May-Oct",          "A holy alpine lake trek in the Langtang region, sacred to both Hindus and Buddhists.",                                                                                 round(499.00  * _EXCHANGE_RATE, 2), 4380, "Sacred alpine lakes, Laurebina Pass, views of Ganesh Himal"),
        (11, "Rara Lake Wilderness",       "hike",     "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&w=1200&q=80",  "Moderate",    9,  "Mar-May, Sep-Nov", "Trek through the untouched forests of western Nepal to the largest and deepest freshwater lake in the country.",                                                      round(1499.00 * _EXCHANGE_RATE, 2), 2990, "Pristine pine forests, bird watching, boating on Rara Lake"),
        (12, "Makalu Base Camp",           "basecamp", "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80",  "Challenging", 18, "Sep-Nov, Mar-May", "A challenging journey through the Makalu Barun National Park to the base of the world's fifth-highest peak.",                                                         round(2099.00 * _EXCHANGE_RATE, 2), 4870, "Barun river valley, hanging glaciers, granite cliffs"),
        (13, "Upper Dolpo Wilderness",     "cultural", "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1200&q=80",  "Challenging", 21, "Jun-Sep",          "A high-altitude, trans-Himalayan trek in the isolated Shey Phoksundo National Park, featuring Bon Buddhist heritage.",                                                 round(3499.00 * _EXCHANGE_RATE, 2), 5130, "Phoksundo Lake, Shey Gompa, snow leopard habitats"),
        (14, "Nar Phu Valley",             "cultural", "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",  "Challenging", 11, "Sep-Nov, Mar-May", "Explore the hidden Tibetan valleys of Nar and Phu, with ancient stone villages and high pass crossings.",                                                             round(749.00  * _EXCHANGE_RATE, 2), 5320, "Kang La Pass, ancient fortified villages, unique monasteries"),
        (15, "Everest Three Passes",       "basecamp", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",  "Challenging", 19, "Mar-May, Sep-Nov", "The ultimate Khumbu adventure crossing three high passes: Renjo La, Cho La, and Kongma La.",                                                                           round(1999.00 * _EXCHANGE_RATE, 2), 5535, "Kongma La, Cho La, Renjo La, Gokyo lakes, Everest Base Camp"),
        (16, "Annapurna Base Camp",        "basecamp", "https://images.unsplash.com/photo-1585409677983-0f6c41ca9c3b?auto=format&fit=crop&w=1200&q=80",  "Moderate",    10, "Mar-May, Sep-Nov", "Trek through rhododendron forests and glacial moraines to reach the dramatic amphitheatre of the Annapurna Sanctuary at 4,130m.",                                     round(849.00  * _EXCHANGE_RATE, 2), 4130, "Annapurna Sanctuary, Machapuchare Base Camp, stunning glacial views"),
    ]
    cursor.executemany(
        """
        INSERT IGNORE INTO destinations
            (id, name, category, image_url, difficulty, duration_days, season,
             description, price_per_person, altitude_meters, highlights)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        rows,
    )
