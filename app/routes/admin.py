from flask import Blueprint

from app.controllers.ControllerAdmin import AdminController


class AdminRoutes:
    """Registers all /admin/* routes onto a Blueprint named 'admin'."""

    def __init__(self):
        self.bp = Blueprint("admin", __name__, url_prefix="/admin")
        self.ctrl = AdminController()

    def register(self):
        bp = self.bp
        ctrl = self.ctrl

        # Auth
        bp.route("/login",  methods=["GET", "POST"])(ctrl.login)
        bp.route("/logout")(ctrl.logout)

        # Dashboard
        bp.route("/dashboard")(ctrl.dashboard)
        bp.route("/")(ctrl.dashboard)         # /admin/ → dashboard

        # Destinations
        bp.route("/destinations")(ctrl.destinations)
        bp.route("/destinations/new")(ctrl.destination_new)
        bp.route("/destinations/create", methods=["POST"])(ctrl.destination_create)
        bp.route("/destinations/<int:dest_id>/edit")(ctrl.destination_edit)
        bp.route("/destinations/<int:dest_id>/update", methods=["POST"])(ctrl.destination_update)
        bp.route("/destinations/<int:dest_id>/delete", methods=["POST"])(ctrl.destination_delete)

        # Users
        bp.route("/users")(ctrl.users)
        bp.route("/users/<int:user_id>/toggle-admin", methods=["POST"])(ctrl.user_toggle_admin)
        bp.route("/users/<int:user_id>/delete",       methods=["POST"])(ctrl.user_delete)

        # Reviews
        bp.route("/reviews")(ctrl.reviews)
        bp.route("/reviews/<int:review_id>/delete", methods=["POST"])(ctrl.review_delete)

        # Announcements
        bp.route("/announcements")(ctrl.announcements)
        bp.route("/announcements/create",              methods=["POST"])(ctrl.announcement_create)
        bp.route("/announcements/<int:ann_id>/edit")(ctrl.announcement_edit)
        bp.route("/announcements/<int:ann_id>/update", methods=["POST"])(ctrl.announcement_update)
        bp.route("/announcements/<int:ann_id>/delete", methods=["POST"])(ctrl.announcement_delete)

        # Homepage content
        bp.route("/homepage")(ctrl.homepage_content)
        bp.route("/homepage/<section_key>/update", methods=["POST"])(ctrl.homepage_section_update)

        # Photos
        bp.route("/photos")(ctrl.photos)
        bp.route("/photos/add",                   methods=["POST"])(ctrl.photo_add)
        bp.route("/photos/<int:photo_id>/delete", methods=["POST"])(ctrl.photo_delete)
        bp.route("/photos/<int:photo_id>/toggle", methods=["POST"])(ctrl.photo_toggle)

        return bp
