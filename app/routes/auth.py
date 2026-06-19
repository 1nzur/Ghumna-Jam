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

        self.bp.route("/trip-history")(
            self.controller.trip_history
        )

        self.bp.route("/trip/<int:trip_id>")(
            self.controller.trip_detail
        )

        self.bp.route("/checklist")(
            self.controller.packing_checklist
        )

        self.bp.route("/recommendations")(
            self.controller.recommendations
        )

        self.bp.route("/cost-breakdown")(
            self.controller.cost_breakdown
        )

        self.bp.route("/api/cost-plans", methods=["GET", "POST"])(
            self.controller.api_cost_plans
        )

        self.bp.route("/api/cost-plans/<int:plan_id>", methods=["DELETE"])(
            self.controller.api_delete_cost_plan
        )

        self.bp.route("/about-us")(
            self.controller.about_us
        )

        self.bp.route("/badges")(
            self.controller.badges
        )

        self.bp.route("/follow")(
            self.controller.follow_page
        )

        self.bp.route("/trekker/<int:user_id>")(
            self.controller.trekker_profile
        )

        self.bp.route("/follow/<int:user_id>", methods=["POST"])(
            self.controller.toggle_follow
        )

        self.bp.route("/activity", methods=["POST"])(
            self.controller.post_activity
        )

        self.bp.route("/my-reviews")(
            self.controller.my_reviews
        )

        self.bp.route("/my-reviews/<int:review_id>/edit", methods=["POST"])(
            self.controller.edit_review
        )

        self.bp.route("/my-reviews/<int:review_id>/delete", methods=["POST"])(
            self.controller.delete_review
        )

        self.bp.route("/reviews/<int:review_id>/reply", methods=["POST"])(
            self.controller.reply_to_review
        )

        self.bp.route("/destination/<int:dest_id>/photos", methods=["POST"])(
            self.controller.upload_trek_photo
        )

        self.bp.route("/photos/<int:photo_id>/delete", methods=["POST"])(
            self.controller.delete_photo
        )

        self.bp.route("/checklist/add", methods=["POST"])(
            self.controller.add_checklist_item
        )

        self.bp.route("/checklist/<int:item_id>/toggle", methods=["POST"])(
            self.controller.toggle_checklist_item
        )

        self.bp.route("/checklist/<int:item_id>/delete", methods=["POST"])(
            self.controller.delete_checklist_item
        )

        self.bp.route("/api/sos", methods=["POST"])(
            self.controller.create_sos_alert
        )

        self.bp.route("/api/complete-trek", methods=["POST"])(
            self.controller.complete_trek
        )

        return self.bp
