from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User

auth = Blueprint("auth", __name__)

# ======================
# REGISTER
# ======================
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        # check if email exists
        existing_user = User.query.filter_by(email=request.form["email"]).first()
        if existing_user:
            return "Email already exists"

        # hash password
        hashed_password = generate_password_hash(request.form["password"])

        # create user
        user = User(
            name=request.form["name"],
            email=request.form["email"],
            password=hashed_password,
            role=request.form["role"]
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# ======================
# LOGIN
# ======================
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect("/dashboard")

        return "Login failed"

    return render_template("login.html")


# ======================
# LOGOUT
# ======================
@auth.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/login")


# ======================
# LANGUAGE SWITCH
# ======================
@auth.route("/set_language/<lang>")
def set_language(lang):
    session["lang"] = lang
    return redirect(request.referrer or "/")