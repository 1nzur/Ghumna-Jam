import pymysql
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash

from app.models.database import get_db


class BaseModel:
    @staticmethod
    def get_user_by_email(email):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, full_name, email, password_hash, phone_number,
                       date_of_birth, profile_picture_url, is_admin
                FROM users
                WHERE email = %s
                """,
                (email,),
            )
            return cursor.fetchone()

    @staticmethod
    def authenticate_user(email, password):
        user = BaseModel.get_user_by_email(email)
        if user is None:
            return None

        if not check_password_hash(user["password_hash"], password):
            return None

        return user

    @staticmethod
    def get_user_by_id(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, full_name, email, password_hash, phone_number, date_of_birth, profile_picture_url
                FROM users
                WHERE id = %s
                """,
                (user_id,),
            )
            return cursor.fetchone()

    @staticmethod
    def update_user(
        user_id,
        full_name,
        email,
        phone_number=None,
        date_of_birth=None,
        profile_picture_url=None,
        password=None,
    ):
        db = get_db()

        try:
            with db.cursor() as cursor:
                if password:
                    cursor.execute(
                        """
                        UPDATE users
                        SET full_name = %s,
                            email = %s,
                            phone_number = %s,
                            date_of_birth = %s,
                            profile_picture_url = %s,
                            password_hash = %s
                        WHERE id = %s
                        """,
                        (
                            full_name,
                            email,
                            phone_number,
                            date_of_birth or None,
                            profile_picture_url,
                            generate_password_hash(password),
                            user_id,
                        ),
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE users
                        SET full_name = %s,
                            email = %s,
                            phone_number = %s,
                            date_of_birth = %s,
                            profile_picture_url = %s
                        WHERE id = %s
                        """,
                        (
                            full_name,
                            email,
                            phone_number,
                            date_of_birth or None,
                            profile_picture_url,
                            user_id,
                        ),
                    )
            db.commit()
        except pymysql.err.IntegrityError as exc:
            db.rollback()
            if exc.args and exc.args[0] == 1062:
                raise ValueError("That email is already used by another account.") from exc
            raise

    @staticmethod
    def create_booking(user_id, dest_name, dest_image, status, departure_date,
                       travelers_count, duration_days, difficulty, selected_hotel, total_price):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO bookings (user_id, dest_name, dest_image, status, departure_date,
                                      travelers_count, duration_days, difficulty, selected_hotel, total_price)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, dest_name, dest_image, status, departure_date,
                 travelers_count, duration_days, difficulty, selected_hotel, total_price),
            )
        db.commit()

    @staticmethod
    def get_bookings_by_user(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, dest_name, dest_image, status, departure_date,
                       travelers_count, duration_days, difficulty, selected_hotel, total_price, booked_at
                FROM bookings
                WHERE user_id = %s
                ORDER BY booked_at DESC
                """,
                (user_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def create_user(full_name, email, password):
        db = get_db()
        password_hash = generate_password_hash(password)

        try:
            with db.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (full_name, email, password_hash)
                    VALUES (%s, %s, %s)
                    """,
                    (full_name, email, password_hash),
                )
            db.commit()
        except pymysql.err.IntegrityError as exc:
            db.rollback()
            if exc.args and exc.args[0] == 1062:
                raise ValueError("An account with this email already exists.") from exc
            raise

    @staticmethod
    def get_user_by_reset_token(token):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, full_name, email, reset_token_expires
                FROM users
                WHERE reset_token = %s
                """,
                (token,),
            )
            user = cursor.fetchone()
            if not user:
                return None
            expires = user.get("reset_token_expires")
            if expires is None or expires < datetime.utcnow():
                return None
            return user

    @staticmethod
    def save_reset_token(email, token):
        db = get_db()
        expires = datetime.utcnow() + timedelta(hours=1)
        with db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users
                SET reset_token = %s, reset_token_expires = %s
                WHERE email = %s
                """,
                (token, expires, email),
            )
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def update_password(user_id, password):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users
                SET password_hash = %s,
                    reset_token = NULL,
                    reset_token_expires = NULL
                WHERE id = %s
                """,
                (generate_password_hash(password), user_id),
            )
        db.commit()

    @staticmethod
    def cancel_booking(user_id, booking_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE bookings
                SET status = 'Cancelled'
                WHERE id = %s AND user_id = %s
                """,
                (booking_id, user_id),
            )
        db.commit()

    # ── Favorites & Reviews (stubs used by destination_detail) ────────────

    @staticmethod
    def get_favorite_destination_ids(user_id):
        try:
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT dest_id FROM favorites WHERE user_id=%s", (user_id,)
                )
                return [row["dest_id"] for row in cursor.fetchall()]
        except Exception:
            return []

    @staticmethod
    def add_favorite_destination(user_id, dest_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "INSERT IGNORE INTO favorites (user_id, dest_id) VALUES (%s,%s)",
                (user_id, dest_id),
            )
        db.commit()

    @staticmethod
    def remove_favorite_destination(user_id, dest_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "DELETE FROM favorites WHERE user_id=%s AND dest_id=%s",
                (user_id, dest_id),
            )
        db.commit()

    @staticmethod
    def get_user_favorites(user_id):
        return []

    @staticmethod
    def get_destination_rating(dest_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT AVG(rating) AS avg_r, COUNT(*) AS cnt FROM destination_reviews WHERE dest_id=%s",
                (dest_id,),
            )
            row = cursor.fetchone()
            return (float(row["avg_r"]) if row["avg_r"] else 0.0, int(row["cnt"]))

    @staticmethod
    def get_reviews_for_destination(dest_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT dr.id, dr.user_id, dr.rating, dr.comment, dr.created_at, dr.updated_at,
                       u.full_name
                FROM destination_reviews dr
                JOIN users u ON u.id = dr.user_id
                WHERE dr.dest_id = %s
                ORDER BY dr.created_at DESC
                """,
                (dest_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def get_user_review_for_dest(user_id, dest_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT id, rating, comment, created_at, updated_at FROM destination_reviews WHERE user_id=%s AND dest_id=%s",
                (user_id, dest_id),
            )
            return cursor.fetchone()

    @staticmethod
    def add_destination_review(user_id, dest_id, rating, comment):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "INSERT INTO destination_reviews (user_id, dest_id, rating, comment) VALUES (%s,%s,%s,%s)",
                (user_id, dest_id, rating, comment),
            )
        db.commit()

    @staticmethod
    def update_destination_review(user_id, review_id, rating, comment):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE destination_reviews
                SET rating=%s, comment=%s
                WHERE id=%s AND user_id=%s
                """,
                (rating, comment, review_id, user_id),
            )
        db.commit()

    @staticmethod
    def can_review_destination(user_id, dest_name):
        """True if the user has logged this trek as completed."""
        return BaseModel.has_logged_trek(user_id, dest_name)

    # ── Achievement Badges ─────────────────────────────────────────────────

    BADGE_DEFINITIONS = [
        # Milestone badges
        {"slug": "first_step",         "name": "First Step",         "icon": "🥾", "desc": "Complete your very first trek",              "category": "Milestone"},
        {"slug": "trio_peaks",         "name": "Trio Peaks",         "icon": "🏔️", "desc": "Complete 3 treks",                           "category": "Milestone"},
        {"slug": "pentacle",           "name": "Pentacle",           "icon": "⛰️", "desc": "Complete 5 treks",                           "category": "Milestone"},
        {"slug": "legend",             "name": "Legend",             "icon": "🌟", "desc": "Complete 10 treks",                          "category": "Milestone"},
        # Difficulty badges
        {"slug": "easy_rider",         "name": "Easy Rider",         "icon": "🌿", "desc": "Complete an Easy difficulty trek",           "category": "Difficulty"},
        {"slug": "moderate_master",    "name": "Moderate Master",    "icon": "🧗", "desc": "Complete a Moderate difficulty trek",        "category": "Difficulty"},
        {"slug": "challenge_accepted", "name": "Challenge Accepted", "icon": "🦁", "desc": "Complete a Challenging difficulty trek",     "category": "Difficulty"},
        {"slug": "high_five",          "name": "High Five",          "icon": "🎯", "desc": "Complete 3 Challenging treks",               "category": "Difficulty"},
        {"slug": "globetrotter",       "name": "Globetrotter",       "icon": "🌏", "desc": "Complete treks across all 3 difficulty levels","category": "Difficulty"},
        # Endurance badges
        {"slug": "endurance",          "name": "Endurance",          "icon": "📅", "desc": "Accumulate 30+ total days trekking",         "category": "Endurance"},
        {"slug": "marathon",           "name": "Marathon Trekker",   "icon": "🗓️", "desc": "Accumulate 60+ total days trekking",         "category": "Endurance"},
        {"slug": "century",            "name": "Century Explorer",   "icon": "💯", "desc": "Accumulate 100+ total days trekking",        "category": "Endurance"},
        # Destination badges
        {"slug": "everest_dreamer",    "name": "Everest Dreamer",    "icon": "👑", "desc": "Complete the Everest Base Camp trek",        "category": "Destination"},
        {"slug": "annapurna_veteran",  "name": "Annapurna Veteran",  "icon": "🏅", "desc": "Complete the Annapurna Circuit trek",        "category": "Destination"},
    ]

    @staticmethod
    def get_completed_trek_stats(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT dest_name, difficulty, duration_days FROM trek_logs WHERE user_id=%s",
                (user_id,),
            )
            rows = cursor.fetchall()
        return {
            "total_completed":   len(rows),
            "easy_count":        sum(1 for r in rows if r["difficulty"] == "Easy"),
            "moderate_count":    sum(1 for r in rows if r["difficulty"] == "Moderate"),
            "challenging_count": sum(1 for r in rows if r["difficulty"] == "Challenging"),
            "total_days":        sum(r["duration_days"] or 0 for r in rows),
            "dest_names":        [r["dest_name"] for r in rows],
        }

    @staticmethod
    def log_trek_completion(user_id, dest_name, difficulty, duration_days):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "INSERT INTO trek_logs (user_id, dest_name, difficulty, duration_days) VALUES (%s, %s, %s, %s)",
                (user_id, dest_name, difficulty, int(duration_days)),
            )
        db.commit()

    @staticmethod
    def has_logged_trek(user_id, dest_name):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM trek_logs WHERE user_id=%s AND dest_name=%s LIMIT 1",
                (user_id, dest_name),
            )
            return cursor.fetchone() is not None

    @staticmethod
    def get_earned_badge_slugs(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT badge_slug FROM user_badges WHERE user_id=%s", (user_id,))
            return {row["badge_slug"] for row in cursor.fetchall()}

    @staticmethod
    def get_user_badges(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT badge_slug, earned_at FROM user_badges WHERE user_id=%s ORDER BY earned_at",
                (user_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def _badge_earned(slug, stats):
        if slug == "first_step":         return stats["total_completed"] >= 1
        if slug == "trio_peaks":         return stats["total_completed"] >= 3
        if slug == "pentacle":           return stats["total_completed"] >= 5
        if slug == "legend":             return stats["total_completed"] >= 10
        if slug == "easy_rider":         return stats["easy_count"] >= 1
        if slug == "moderate_master":    return stats["moderate_count"] >= 1
        if slug == "challenge_accepted": return stats["challenging_count"] >= 1
        if slug == "high_five":          return stats["challenging_count"] >= 3
        if slug == "globetrotter":       return stats["easy_count"] >= 1 and stats["moderate_count"] >= 1 and stats["challenging_count"] >= 1
        if slug == "endurance":          return stats["total_days"] >= 30
        if slug == "marathon":           return stats["total_days"] >= 60
        if slug == "century":            return stats["total_days"] >= 100
        if slug == "everest_dreamer":    return any("Everest Base Camp" in n for n in stats["dest_names"])
        if slug == "annapurna_veteran":  return any("Annapurna Circuit" in n for n in stats["dest_names"])
        return False

    @staticmethod
    def badge_progress(slug, stats):
        """Returns (current, target) for a badge."""
        if slug == "first_step":         return (min(stats["total_completed"], 1), 1)
        if slug == "trio_peaks":         return (min(stats["total_completed"], 3), 3)
        if slug == "pentacle":           return (min(stats["total_completed"], 5), 5)
        if slug == "legend":             return (min(stats["total_completed"], 10), 10)
        if slug == "easy_rider":         return (min(stats["easy_count"], 1), 1)
        if slug == "moderate_master":    return (min(stats["moderate_count"], 1), 1)
        if slug == "challenge_accepted": return (min(stats["challenging_count"], 1), 1)
        if slug == "high_five":          return (min(stats["challenging_count"], 3), 3)
        if slug == "endurance":          return (min(stats["total_days"], 30), 30)
        if slug == "marathon":           return (min(stats["total_days"], 60), 60)
        if slug == "century":            return (min(stats["total_days"], 100), 100)
        if slug == "everest_dreamer":    return (1 if any("Everest Base Camp" in n for n in stats["dest_names"]) else 0, 1)
        if slug == "annapurna_veteran":  return (1 if any("Annapurna Circuit" in n for n in stats["dest_names"]) else 0, 1)
        if slug == "globetrotter":
            levels = (1 if stats["easy_count"] >= 1 else 0) + (1 if stats["moderate_count"] >= 1 else 0) + (1 if stats["challenging_count"] >= 1 else 0)
            return (levels, 3)
        return (0, 1)

    @staticmethod
    def check_and_award_new_badges(user_id):
        """Awards any newly earned badges. Returns list of newly awarded badge dicts."""
        stats = BaseModel.get_completed_trek_stats(user_id)
        already = BaseModel.get_earned_badge_slugs(user_id)
        newly_earned = []
        db = get_db()
        with db.cursor() as cursor:
            for badge in BaseModel.BADGE_DEFINITIONS:
                slug = badge["slug"]
                if slug in already:
                    continue
                if BaseModel._badge_earned(slug, stats):
                    cursor.execute(
                        "INSERT IGNORE INTO user_badges (user_id, badge_slug) VALUES (%s, %s)",
                        (user_id, slug),
                    )
                    newly_earned.append(badge)
        db.commit()
        return newly_earned

    @staticmethod
    def mark_booking_completed(user_id, booking_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "UPDATE bookings SET status='Completed' WHERE id=%s AND user_id=%s AND status='Confirmed'",
                (booking_id, user_id),
            )
        db.commit()

    # ── Notifications ──────────────────────────────────────────────────────

    @staticmethod
    def add_notification(user_id, message):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "INSERT INTO notifications (user_id, message) VALUES (%s, %s)",
                (user_id, message),
            )
        db.commit()

    @staticmethod
    def get_notifications(user_id, limit=20):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT id, message, is_read, created_at FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT %s",
                (user_id, limit),
            )
            return cursor.fetchall()

    @staticmethod
    def get_unread_notification_count(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM notifications WHERE user_id=%s AND is_read=0",
                (user_id,),
            )
            return cursor.fetchone()["cnt"]

    @staticmethod
    def mark_all_notifications_read(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "UPDATE notifications SET is_read=1 WHERE user_id=%s AND is_read=0",
                (user_id,),
            )
        db.commit()

    # ── Packing Checklist ──────────────────────────────────────────────────

    PREDEFINED_ITEMS = [
        ("Trekking boots", "Footwear"),
        ("Gaiters", "Footwear"),
        ("Wool / thermal socks (×5)", "Footwear"),
        ("Down jacket", "Clothing"),
        ("Fleece mid-layer", "Clothing"),
        ("Waterproof rain jacket", "Clothing"),
        ("Trekking trousers (×2)", "Clothing"),
        ("Base-layer thermal top & bottom", "Clothing"),
        ("Warm hat / balaclava", "Clothing"),
        ("Sun hat", "Clothing"),
        ("Gloves (liner + outer)", "Clothing"),
        ("Trekking poles", "Equipment"),
        ("Headlamp + spare batteries", "Equipment"),
        ("Sleeping bag (−10 °C rated)", "Equipment"),
        ("Trekking backpack (50–60 L)", "Equipment"),
        ("Daypack (20–25 L)", "Equipment"),
        ("Trekking map / GPS device", "Equipment"),
        ("Sunglasses (UV400)", "Equipment"),
        ("Water bottles / hydration bladder", "Equipment"),
        ("Water purification tablets / filter", "Equipment"),
        ("First-aid kit", "Health & Safety"),
        ("Altitude sickness medication (Diamox)", "Health & Safety"),
        ("Blister care / moleskin", "Health & Safety"),
        ("Sunscreen SPF 50+", "Health & Safety"),
        ("Lip balm with SPF", "Health & Safety"),
        ("Hand sanitiser", "Health & Safety"),
        ("Personal medications", "Health & Safety"),
        ("Trekking permit / TIMS card", "Documents"),
        ("Passport + copies", "Documents"),
        ("Travel insurance documents", "Documents"),
        ("Emergency contact card", "Documents"),
        ("Cash (NPR) + small USD", "Documents"),
        ("Energy bars / trail mix", "Food & Nutrition"),
        ("Electrolyte sachets", "Food & Nutrition"),
        ("Reusable cutlery & cup", "Food & Nutrition"),
        ("Trekking towel (microfibre)", "Hygiene"),
        ("Toilet paper + waste bags", "Hygiene"),
        ("Biodegradable soap / shampoo", "Hygiene"),
        ("Toothbrush & toothpaste", "Hygiene"),
        ("Power bank (20 000 mAh)", "Electronics"),
        ("Universal travel adapter", "Electronics"),
        ("Camera / extra memory cards", "Electronics"),
    ]

    @staticmethod
    def get_checklist(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM checklist_items WHERE user_id = %s",
                (user_id,),
            )
            row = cursor.fetchone()
            if row["cnt"] == 0:
                BaseModel._seed_checklist(user_id, db, cursor)
            cursor.execute(
                """
                SELECT id, item_name AS name, category, is_checked
                FROM checklist_items
                WHERE user_id = %s
                ORDER BY category, item_name
                """,
                (user_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def _seed_checklist(user_id, db, cursor):
        for name, category in BaseModel.PREDEFINED_ITEMS:
            cursor.execute(
                "INSERT INTO checklist_items (user_id, item_name, category) VALUES (%s, %s, %s)",
                (user_id, name, category),
            )
        db.commit()

    @staticmethod
    def add_checklist_item(user_id, name, category):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "INSERT INTO checklist_items (user_id, item_name, category) VALUES (%s, %s, %s)",
                (user_id, name.strip(), category.strip() or "General"),
            )
        db.commit()

    @staticmethod
    def update_checklist_item(user_id, item_id, name, category):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE checklist_items
                SET item_name = %s, category = %s
                WHERE id = %s AND user_id = %s
                """,
                (name.strip(), category.strip() or "General", item_id, user_id),
            )
        db.commit()

    @staticmethod
    def toggle_checklist_item(user_id, item_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE checklist_items
                SET is_checked = NOT is_checked
                WHERE id = %s AND user_id = %s
                """,
                (item_id, user_id),
            )
        db.commit()

    @staticmethod
    def delete_checklist_item(user_id, item_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "DELETE FROM checklist_items WHERE id = %s AND user_id = %s",
                (item_id, user_id),
            )
        db.commit()

    @staticmethod
    def reset_checklist(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "DELETE FROM checklist_items WHERE user_id = %s",
                (user_id,),
            )
            BaseModel._seed_checklist(user_id, db, cursor)
