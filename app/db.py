import sqlite3
import pymysql
import pymysql.cursors
from app.config import Config

DEFAULT_DESTINATIONS = [
    (
        "Everest Base Camp",
        "Hard",
        14,
        1500.0,
        "The most iconic path across the roof of the world, leading to the foot of Mount Everest.",
        "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=600&q=80",
        "Autumn",
    ),
    (
        "Annapurna Circuit",
        "Moderate",
        18,
        1200.0,
        "A classic trek offering incredibly diverse landscapes, from lush sub-tropical forests to alpine meadows.",
        "https://images.unsplash.com/photo-1501555088652-021faa106b9b?auto=format&fit=crop&w=600&q=80",
        "Spring",
    ),
    (
        "Langtang Valley",
        "Easy",
        8,
        800.0,
        "A stunning valley trek rich in culture, ancient monasteries, and spectacular mountain views close to Kathmandu.",
        "https://images.unsplash.com/photo-1486915309851-b0cc1f8a0084?auto=format&fit=crop&w=600&q=80",
        "Spring",
    ),
    (
        "Mardi Himal",
        "Moderate",
        5,
        520.0,
        "A compact ridge-line trek with close views of Machhapuchhre and quiet forest camps above Pokhara.",
        "https://images.unsplash.com/photo-1533130061792-64b345e4a833?auto=format&fit=crop&w=600&q=80",
        "Autumn",
    ),
    (
        "Gosaikunda Lakes",
        "Moderate",
        6,
        640.0,
        "A sacred alpine lake route with dramatic passes, rhododendron forests, and wide Langtang panoramas.",
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=600&q=80",
        "Spring",
    ),
    (
        "Upper Mustang",
        "Hard",
        12,
        1800.0,
        "A remote trans-Himalayan journey through wind-carved cliffs, cave settlements, and Tibetan-influenced villages.",
        "https://images.unsplash.com/photo-1526772662000-3f88f10405ff?auto=format&fit=crop&w=600&q=80",
        "Autumn",
    ),
]


def get_db_connection():
    """
    Returns a connection and a cursor object based on DB_TYPE in Config.
    The cursor will return dictionaries (or dictionary-like Row objects) for query results.
    """
    if Config.DB_TYPE == 'mysql':
        try:
            conn = pymysql.connect(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                db=Config.MYSQL_DB,
                cursorclass=pymysql.cursors.DictCursor
            )
            return conn, conn.cursor()
        except pymysql.MySQLError as e:
            # Fall back to sqlite if MySQL connection fails
            print(f"MySQL connection failed: {e}. Falling back to SQLite.")
    
    # SQLite fallback / default
    conn = sqlite3.connect(Config.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn, conn.cursor()

def execute_query(query, params=None, commit=False):
    """
    Executes a query and returns:
    - For SELECT: a list of dictionaries
    - For INSERT with commit=True: the last inserted row ID
    - For UPDATE/DELETE: affected row count
    """
    conn, cursor = get_db_connection()
    results = None
    try:
        # SQLite uses '?' as placeholder, MySQL uses '%s'.
        # We write queries with '%s' or we write a converter.
        # To make it simple, let's write queries with '?' placeholders and convert them to '%s' if MySQL is used.
        if Config.DB_TYPE == 'mysql' and isinstance(conn, pymysql.connections.Connection):
            query = query.replace('?', '%s')
            
        cursor.execute(query, params or ())
        
        if commit:
            conn.commit()
            if query.strip().upper().startswith('INSERT'):
                results = cursor.lastrowid
            else:
                results = cursor.rowcount
        else:
            rows = cursor.fetchall()
            # If SQLite, convert sqlite3.Row to standard dicts
            if isinstance(conn, sqlite3.Connection):
                results = [dict(row) for row in rows]
            else:
                results = list(rows)
    except Exception as e:
        print(f"Database error: {e}")
        if commit:
            conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
    return results

def init_db():
    """
    Creates tables and seeds default destinations.
    """
    # 1. Create Tables
    # SQLite/MySQL compatible schema definition
    users_table_sqlite = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    destinations_table_sqlite = """
    CREATE TABLE IF NOT EXISTS destinations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        duration_days INTEGER NOT NULL,
        price_per_person REAL NOT NULL,
        description TEXT NOT NULL,
        image_url TEXT,
        season TEXT NOT NULL
    );
    """
    
    bookings_table_sqlite = """
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        destination_id INTEGER NOT NULL,
        departure_date TEXT NOT NULL,
        travelers_count INTEGER NOT NULL,
        total_price REAL NOT NULL,
        status TEXT DEFAULT 'Confirmed',
        booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (destination_id) REFERENCES destinations (id)
    );
    """

    conn, cursor = get_db_connection()
    try:
        if Config.DB_TYPE == 'mysql' and isinstance(conn, pymysql.connections.Connection):
            # MySQL-specific types
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS destinations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                difficulty VARCHAR(50) NOT NULL,
                duration_days INT NOT NULL,
                price_per_person DECIMAL(10,2) NOT NULL,
                description TEXT NOT NULL,
                image_url VARCHAR(500),
                season VARCHAR(50) NOT NULL
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                destination_id INT NOT NULL,
                departure_date VARCHAR(50) NOT NULL,
                travelers_count INT NOT NULL,
                total_price DECIMAL(10,2) NOT NULL,
                status VARCHAR(50) DEFAULT 'Confirmed',
                booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (destination_id) REFERENCES destinations(id)
            );
            """)
        else:
            # SQLite
            cursor.execute(users_table_sqlite)
            cursor.execute(destinations_table_sqlite)
            cursor.execute(bookings_table_sqlite)
        conn.commit()
    except Exception as e:
        print(f"Table creation error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    # 2. Seed default destinations without disturbing existing bookings.
    existing_rows = execute_query("SELECT name FROM destinations")
    existing_names = {row["name"] for row in existing_rows}
    missing_destinations = [
        destination
        for destination in DEFAULT_DESTINATIONS
        if destination[0] not in existing_names
    ]

    if missing_destinations:
        print(f"Seeding {len(missing_destinations)} destination(s)...")
        for dest in missing_destinations:
            execute_query(
                "INSERT INTO destinations (name, difficulty, duration_days, price_per_person, description, image_url, season) VALUES (?, ?, ?, ?, ?, ?, ?)",
                dest,
                commit=True
            )
        print("Default destinations seeded.")
