import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-ghumna-jam-change-me")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    
    DB_TYPE = os.environ.get("DB_TYPE", "sqlite").lower()
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SQLITE_DB_PATH = os.environ.get(
        "SQLITE_DB_PATH",
        os.path.join(BASE_DIR, "db.sqlite"),
    )
    
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DB = os.environ.get("MYSQL_DB", "ghumnajam")


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLITE_DB_PATH = ":memory:"
