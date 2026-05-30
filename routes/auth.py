from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from extensions import db, mail
from models import User

auth_bp = Blueprint("auth", __name__)

def get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

# Login
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["username"] = username
            return redirect(url_for("dashboard.dashboard"))

        flash("Invalid username or password!", "error")
        return redirect(url_for("auth.login"))

    return render_template("login.html")

# Register
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form["fullname"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Username already exists!", "error")
            return redirect(url_for("auth.register"))

        if existing_email:
            flash("Email already exists!", "error")
            return redirect(url_for("auth.register"))

        new_user = User(fullname=fullname, email=email, username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        session["username"] = username
        flash("Registration successful!", "success")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("register.html")

# Logout
@auth_bp.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("auth.login"))

# Forgot Password
@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("No account found with that email.", "error")
            return redirect(url_for("auth.forgot_password"))

        serializer = get_serializer()
        token = serializer.dumps(user.email, salt="password-reset-salt")
        reset_url = url_for("auth.reset_password", token=token, _external=True)

        msg = Message("Password Reset Request", recipients=[user.email])
        msg.body = (
            f"Hello {user.fullname},\n\n"
            f"Click the link below to reset your password:\n{reset_url}\n\n"
            f"If you did not request this, ignore this email."
        )
        mail.send(msg)

        flash("Password reset link sent to your email.", "success")
        return redirect(url_for("auth.forgot_password"))

    return render_template("forgot-password.html")

# Reset Password
@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    serializer = get_serializer()

    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=3600)
    except (SignatureExpired, BadSignature):
        flash("The reset link is invalid or has expired.", "error")
        return redirect(url_for("auth.forgot_password"))

    user = User.query.filter_by(email=email).first()

    if request.method == "POST":
        new_password = request.form["newPassword"]
        confirm_password = request.form["confirmPassword"]

        if new_password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth.reset_password", token=token))

        user.set_password(new_password)
        db.session.commit()
        flash("Your password has been reset successfully.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset-password.html")