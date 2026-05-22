from werkzeug.security import generate_password_hash, check_password_hash
from app.db import execute_query

def register_user(name, email, password):
    """
    Registers a new user after hashing the password.
    Returns (success_boolean, message)
    """
    if not name or not email or not password:
        return False, "All fields are required."
    
    # Check if user already exists
    existing = execute_query("SELECT id FROM users WHERE email = ?", (email,))
    if existing:
        return False, "An account with this email address already exists."
    
    # Hash password
    pwd_hash = generate_password_hash(password)
    
    try:
        user_id = execute_query(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, pwd_hash),
            commit=True
        )
        return True, f"Registration successful. User ID: {user_id}"
    except Exception as e:
        return False, f"Database error during registration: {e}"

def authenticate_user(email, password):
    """
    Authenticates a user by email and password.
    Returns (success_boolean, user_dict_or_error_message)
    """
    if not email or not password:
        return False, "Email and password are required."
    
    users = execute_query("SELECT * FROM users WHERE email = ?", (email,))
    if not users:
        return False, "Invalid email or password."
    
    user = users[0]
    if check_password_hash(user['password_hash'], password):
        # Successful authentication. Clear password hash before returning
        user_data = dict(user)
        user_data.pop('password_hash', None)
        return True, user_data
    
    return False, "Invalid email or password."
