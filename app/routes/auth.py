from flask import Blueprint

from app.controllers.ControllerAuth import AuthController


class AuthRoute:
    def __init__(self):
        self.bp = Blueprint("auth", __name__)
        self.controller = AuthController()
        self.register()

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
