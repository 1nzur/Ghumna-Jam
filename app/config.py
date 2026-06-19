import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-ghumna-jam-change-me")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME_DAYS = int(os.environ.get("PERMANENT_SESSION_LIFETIME_DAYS", "14"))

    DB_TYPE = "mysql"

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SQLITE_DB_PATH = os.environ.get("SQLITE_DB_PATH", os.path.join(BASE_DIR, "db.sqlite"))

    try:
        import config as root_config
        MYSQL_HOST = getattr(root_config, "MYSQL_HOST", "localhost")
        MYSQL_USER = getattr(root_config, "MYSQL_USER", "root")
        MYSQL_PASSWORD = getattr(root_config, "MYSQL_PASSWORD", "samul")
        MYSQL_DB = getattr(root_config, "MYSQL_DATABASE", "ghumna_jam")
    except ImportError:
        MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
        MYSQL_USER = os.environ.get("MYSQL_USER", "root")
        MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "samul")
        MYSQL_DB = os.environ.get("MYSQL_DB", "ghumna_jam")
    MYSQL_DATABASE = MYSQL_DB

    WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "")
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(BASE_DIR, "app", "static", "uploads"))


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLITE_DB_PATH = ":memory:"
