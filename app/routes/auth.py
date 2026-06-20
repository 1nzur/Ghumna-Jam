from flask import Blueprint, redirect, url_for

from app.controllers.ControllerAuth import AuthController


class AuthRoutes:
    def __init__(self):
        self.bp = Blueprint("auth", __name__)
        self.controller = AuthController()

    def register(self):
        self.bp.route("/login", methods=["GET", "POST"])(
            self.controller.login
        )

        self.bp.route("/register", methods=["GET", "POST"])(
            self.controller.register
        )

        self.bp.route("/signup", methods=["GET", "POST"])(
            self.controller.signup
        )

        self.bp.route("/terms")(
            self.controller.terms
        )

        self.bp.route("/home")(
            self.controller.home
        )

        self.bp.route("/homepage")(
            self.controller.home
        )

        self.bp.route("/landpage")(
            self.controller.landpage
        )

        # Redirect common mis-typed or old-link URLs to the home page
        @self.bp.route("/destinations")
        @self.bp.route("/home/destinations")
        def destinations_redirect():
            return redirect(url_for("auth.home"))

        self.bp.route("/logout")(
            self.controller.logout
        )

        self.bp.route("/forgot-password", methods=["GET", "POST"])(
            self.controller.forgot_password
        )

        self.bp.route("/reset-password/<token>", methods=["GET", "POST"])(
            self.controller.reset_password
        )

        self.bp.route("/bookings")(
            self.controller.bookings
        )

        self.bp.route("/bookings/cancel/<int:booking_id>", methods=["POST"])(
            self.controller.cancel_booking
        )

        self.bp.route("/favorites")(
            self.controller.favorites
        )

        self.bp.route("/destination/<int:dest_id>")(
            self.controller.destination_detail
        )
        self.bp.route("/destination/<int:dest_id>/favorite", methods=["POST"])(
            self.controller.toggle_favorite
        )
        self.bp.route("/destination/<int:dest_id>/review", methods=["POST"])(
            self.controller.submit_review
        )

        self.bp.route("/destination/<int:dest_id>/review/<int:review_id>/edit", methods=["POST"])(
            self.controller.edit_review
        )
        self.bp.route("/compare")(
            self.controller.compare_treks
        )

        self.bp.route("/book/<int:dest_id>", methods=["POST"])(
            self.controller.book_trip
        )

        self.bp.route("/edit-profile", methods=["GET", "POST"])(
            self.controller.edit_profile
        )

        self.bp.route("/profile", methods=["GET", "POST"])(
            self.controller.edit_profile
        )

        self.bp.route("/tracking", methods=["GET", "POST"])(
            self.controller.tracking
        )

        self.bp.route("/socials")(
            self.controller.socials
        )

        self.bp.route("/destination/<int:dest_id>/log-complete", methods=["POST"])(
            self.controller.log_completion
        )

        self.bp.route("/badges")(
            self.controller.badges
        )

        self.bp.route("/notifications/read", methods=["POST"])(
            self.controller.notifications_read
        )

        self.bp.route("/checklist")(
            self.controller.checklist
        )

        self.bp.route("/checklist/add", methods=["POST"])(
            self.controller.checklist_add
        )

        self.bp.route("/checklist/toggle/<int:item_id>", methods=["POST"])(
            self.controller.checklist_toggle
        )

        self.bp.route("/checklist/edit/<int:item_id>", methods=["POST"])(
            self.controller.checklist_edit
        )

        self.bp.route("/checklist/delete/<int:item_id>", methods=["POST"])(
            self.controller.checklist_delete
        )

        self.bp.route("/checklist/reset", methods=["POST"])(
            self.controller.checklist_reset
        )

        return self.bp
