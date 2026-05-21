from flask import Flask, redirect, render_template, url_for

app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)

@app.route("/")
def home():
    return render_template("landpage.html")

@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/edit-profile")
def signup():
    return render_template("edit-profile.html)

if __name__ == "__main__":
    app.run(debug=True, port=5055)
