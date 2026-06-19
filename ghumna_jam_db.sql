-- Drop the table if it already exists (Uncomment the line below if you want to start fresh)
-- DROP TABLE IF EXISTS users;

-- Create the users table for Ghumna Jam
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone_number VARCHAR(30),
    date_of_birth DATE,
    profile_picture_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

select * from users;
