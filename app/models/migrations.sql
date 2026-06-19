-- MIGRATION SCRIPT FOR NEPAL TREK PLANNING PLATFORM

-- 1. Create Permits & Destination Permits tables
CREATE TABLE IF NOT EXISTS permits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    cost_npr DECIMAL(10,2) NOT NULL DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS destination_permits (
    destination_id INT NOT NULL,
    permit_id INT NOT NULL,
    PRIMARY KEY (destination_id, permit_id),
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE,
    FOREIGN KEY (permit_id) REFERENCES permits(id) ON DELETE CASCADE
);

-- 2. Create Trip History
CREATE TABLE IF NOT EXISTS trip_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    booking_id INT NOT NULL,
    destination_id INT NOT NULL,
    history_status VARCHAR(50) NOT NULL DEFAULT 'Upcoming', -- 'Upcoming', 'Completed', 'Cancelled'
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
);

-- 3. Create Trek Tracking Sessions
CREATE TABLE IF NOT EXISTS trek_tracking_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    trip_id INT, -- optional link to trip_history
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
);

-- 4. Create GPS Route Points
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
);

-- 5. Create Elevation History
CREATE TABLE IF NOT EXISTS elevation_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    altitude DECIMAL(8,2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES trek_tracking_sessions(id) ON DELETE CASCADE
);

-- 6. Create Packing Checklists
CREATE TABLE IF NOT EXISTS packing_checklists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 7. Create Packing Checklist Items
CREATE TABLE IF NOT EXISTS packing_checklist_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    checklist_id INT NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    category VARCHAR(80) NOT NULL DEFAULT 'Gear',
    is_packed TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (checklist_id) REFERENCES packing_checklists(id) ON DELETE CASCADE
);

-- 8. Create Trek Recommendations
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
);

-- 9. Create Review Photos
CREATE TABLE IF NOT EXISTS review_photos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    review_id INT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
);

-- 10. Create User Statistics
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
);

-- 11. Create Trek Statistics
CREATE TABLE IF NOT EXISTS trek_statistics (
    destination_id INT PRIMARY KEY,
    total_bookings INT DEFAULT 0,
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    reviews_count INT DEFAULT 0,
    photos_count INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
);

-- 12. Create Cost Breakdown Records
CREATE TABLE IF NOT EXISTS cost_breakdown_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT, -- optional if tied to booking
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
);

-- 13. Seed Permits Default Data
INSERT IGNORE INTO permits (name, cost_npr) VALUES
('TIMS Card', 2000.00),
('ACAP Permit', 3000.00),
('Sagarmatha Permit', 3000.00),
('Langtang Permit', 3000.00),
('Manaslu Permit', 10000.00),
('Upper Mustang Permit', 70000.00);

-- 14. Seed Achievements Default Data
INSERT IGNORE INTO achievements (slug, name, description, threshold_type, threshold_value) VALUES
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
('fifty-followers', '50 Followers', 'Become a popular guide/trekker with 50 followers.', 'followers', 50);
