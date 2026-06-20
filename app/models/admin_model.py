from app.models.database import get_db


class AdminModel:
    """All database operations used exclusively by the admin panel."""

    # ── Dashboard ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_dashboard_stats():
        """Aggregate counts and recent activity for the overview cards."""
        db = get_db()
        with db.cursor() as cursor:
            stats = {}

            cursor.execute("SELECT COUNT(*) AS cnt FROM users")
            stats["total_users"] = cursor.fetchone()["cnt"]

            cursor.execute("SELECT COUNT(*) AS cnt FROM bookings")
            stats["total_bookings"] = cursor.fetchone()["cnt"]

            cursor.execute("SELECT COUNT(*) AS cnt FROM bookings WHERE status = 'Confirmed'")
            stats["active_bookings"] = cursor.fetchone()["cnt"]

            cursor.execute("SELECT COUNT(*) AS cnt FROM destinations WHERE is_active = 1")
            stats["active_destinations"] = cursor.fetchone()["cnt"]

            cursor.execute("SELECT COUNT(*) AS cnt FROM destination_reviews")
            stats["total_reviews"] = cursor.fetchone()["cnt"]

            cursor.execute("SELECT COUNT(*) AS cnt FROM announcements WHERE is_active = 1")
            stats["active_announcements"] = cursor.fetchone()["cnt"]

            cursor.execute(
                "SELECT COALESCE(SUM(total_price), 0) AS total FROM bookings WHERE status != 'Cancelled'"
            )
            stats["total_revenue"] = float(cursor.fetchone()["total"] or 0)

            cursor.execute(
                """
                SELECT u.full_name, b.dest_name, b.total_price, b.booked_at, b.status
                FROM bookings b JOIN users u ON b.user_id = u.id
                ORDER BY b.booked_at DESC LIMIT 6
                """
            )
            stats["recent_bookings"] = cursor.fetchall()

            cursor.execute(
                "SELECT id, full_name, email, created_at FROM users ORDER BY created_at DESC LIMIT 5"
            )
            stats["recent_users"] = cursor.fetchall()

        return stats

    # ── Destinations ──────────────────────────────────────────────────────────

    @staticmethod
    def get_all_destinations():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM destinations ORDER BY id")
            return cursor.fetchall()

    @staticmethod
    def get_destination_by_id(dest_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM destinations WHERE id = %s", (dest_id,))
            return cursor.fetchone()

    @staticmethod
    def get_active_destinations():
        """Used by the public site to replace the hardcoded list."""
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM destinations WHERE is_active = 1 ORDER BY id"
            )
            return cursor.fetchall()

    @staticmethod
    def create_destination(data):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO destinations
                    (name, category, image_url, difficulty, duration_days, season,
                     description, price_per_person, altitude_meters, highlights, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    data["name"], data["category"], data.get("image_url", ""),
                    data["difficulty"], int(data["duration_days"]),
                    data.get("season", ""), data.get("description", ""),
                    float(data["price_per_person"]), int(data.get("altitude_meters", 0)),
                    data.get("highlights", ""),
                    1 if data.get("is_active", True) else 0,
                ),
            )
        db.commit()

    @staticmethod
    def update_destination(dest_id, data):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE destinations SET
                    name=%s, category=%s, image_url=%s, difficulty=%s,
                    duration_days=%s, season=%s, description=%s,
                    price_per_person=%s, altitude_meters=%s, highlights=%s, is_active=%s
                WHERE id = %s
                """,
                (
                    data["name"], data["category"], data.get("image_url", ""),
                    data["difficulty"], int(data["duration_days"]),
                    data.get("season", ""), data.get("description", ""),
                    float(data["price_per_person"]), int(data.get("altitude_meters", 0)),
                    data.get("highlights", ""),
                    1 if data.get("is_active", True) else 0,
                    dest_id,
                ),
            )
        db.commit()

    @staticmethod
    def delete_destination(dest_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM destinations WHERE id = %s", (dest_id,))
        db.commit()

    # ── Users ─────────────────────────────────────────────────────────────────

    @staticmethod
    def get_all_users():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT u.id, u.full_name, u.email, u.phone_number, u.is_admin,
                       u.created_at,
                       COUNT(b.id) AS booking_count
                FROM users u
                LEFT JOIN bookings b ON b.user_id = u.id
                GROUP BY u.id
                ORDER BY u.created_at DESC
                """
            )
            return cursor.fetchall()

    @staticmethod
    def get_user_by_id(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT id, full_name, email, is_admin, created_at FROM users WHERE id = %s",
                (user_id,),
            )
            return cursor.fetchone()

    @staticmethod
    def set_user_admin(user_id, is_admin):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET is_admin = %s WHERE id = %s",
                (1 if is_admin else 0, user_id),
            )
        db.commit()

    @staticmethod
    def delete_user(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()

    @staticmethod
    def admin_exists():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS cnt FROM users WHERE is_admin = 1")
            return cursor.fetchone()["cnt"] > 0

    # ── Reviews ───────────────────────────────────────────────────────────────

    @staticmethod
    def get_all_reviews():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT r.id, r.dest_id, r.rating, r.comment, r.created_at,
                       u.full_name AS user_name, u.email AS user_email
                FROM destination_reviews r
                JOIN users u ON r.user_id = u.id
                ORDER BY r.created_at DESC
                """
            )
            return cursor.fetchall()

    @staticmethod
    def delete_review(review_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM destination_reviews WHERE id = %s", (review_id,))
        db.commit()

    # ── Announcements ─────────────────────────────────────────────────────────

    @staticmethod
    def get_all_announcements():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT a.*, u.full_name AS created_by_name
                FROM announcements a
                LEFT JOIN users u ON a.created_by = u.id
                ORDER BY a.created_at DESC
                """
            )
            return cursor.fetchall()

    @staticmethod
    def get_announcement_by_id(ann_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM announcements WHERE id = %s", (ann_id,))
            return cursor.fetchone()

    @staticmethod
    def get_active_announcements():
        """Called from public-facing templates to show site banners."""
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM announcements WHERE is_active = 1 ORDER BY created_at DESC"
            )
            return cursor.fetchall()

    @staticmethod
    def create_announcement(title, message, ann_type, is_active, created_by):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO announcements (title, message, type, is_active, created_by)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (title, message, ann_type, 1 if is_active else 0, created_by),
            )
        db.commit()

    @staticmethod
    def update_announcement(ann_id, title, message, ann_type, is_active):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE announcements
                SET title=%s, message=%s, type=%s, is_active=%s
                WHERE id = %s
                """,
                (title, message, ann_type, 1 if is_active else 0, ann_id),
            )
        db.commit()

    @staticmethod
    def delete_announcement(ann_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM announcements WHERE id = %s", (ann_id,))
        db.commit()

    # ── Homepage Content ──────────────────────────────────────────────────────

    @staticmethod
    def get_all_homepage_sections():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM homepage_content ORDER BY section_key")
            return cursor.fetchall()

    @staticmethod
    def get_homepage_section(section_key):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM homepage_content WHERE section_key = %s", (section_key,)
            )
            return cursor.fetchone()

    @staticmethod
    def upsert_homepage_section(section_key, title, subtitle, body, updated_by):
        """Insert or update a homepage content section by its unique key."""
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO homepage_content (section_key, title, subtitle, body, updated_by)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    title      = VALUES(title),
                    subtitle   = VALUES(subtitle),
                    body       = VALUES(body),
                    updated_by = VALUES(updated_by),
                    updated_at = CURRENT_TIMESTAMP
                """,
                (section_key, title, subtitle, body, updated_by),
            )
        db.commit()

    # ── Site Photos ───────────────────────────────────────────────────────────

    @staticmethod
    def get_all_photos():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM site_photos ORDER BY section, sort_order, id"
            )
            return cursor.fetchall()

    @staticmethod
    def get_active_photos_by_section(section):
        """Return active photos for a specific section (e.g. 'gallery', 'hero')."""
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM site_photos WHERE section = %s AND is_active = 1 ORDER BY sort_order, id",
                (section,),
            )
            return cursor.fetchall()

    @staticmethod
    def add_photo(title, image_url, section, uploaded_by):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO site_photos (title, image_url, section, uploaded_by)
                VALUES (%s, %s, %s, %s)
                """,
                (title, image_url, section, uploaded_by),
            )
        db.commit()

    @staticmethod
    def delete_photo(photo_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM site_photos WHERE id = %s", (photo_id,))
        db.commit()

    @staticmethod
    def toggle_photo_active(photo_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "UPDATE site_photos SET is_active = NOT is_active WHERE id = %s",
                (photo_id,),
            )
        db.commit()
