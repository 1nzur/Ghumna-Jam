import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'alpine-heritage-secret-key-1823')
    
    # Database configs - Defaults to SQLite, falls back to MySQL if environment variables are set
    DB_TYPE = os.environ.get('DB_TYPE', 'sqlite') # 'sqlite' or 'mysql'
    
    # SQLite Configuration
    SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db.sqlite')
    
    # MySQL Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'ghumnajam')
