from flask import Blueprint

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

        return self.bp
