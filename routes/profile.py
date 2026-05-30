from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from sqlalchemy.exc import IntegrityError
from extensions import db, mail
from models import User

profile_bp = Blueprint("profile", __name__)

def get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

def send_email_verification(user_id, new_email):
    s = get_serializer()
    token = s.dumps({"user_id": user_id, "new_email": new_email}, salt="email-change-salt")
    verify_link = url_for("profile.verify_email_change", token=token, _external=True)

    msg = Message(
        subject="Verify your new email address",
        recipients=[new_email],
        body=f"Please verify your new email by clicking this link: {verify_link}"
    )
    mail.send(msg)
    return token

@profile_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        session.pop("username", None)
        flash("User not found.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()

        if not fullname or not username or not email:
            flash("All fields are required.", "error")
            return redirect(url_for("profile.profile"))

        if len(username) < 3 or len(username) > 25:
            flash("Username must be between 3 and 25 characters.", "error")
            return redirect(url_for("profile.profile"))

        existing_username = User.query.filter(User.username == username, User.id != user.id).first()
        if existing_username:
            flash("Username already exists.", "error")
            return redirect(url_for("profile.profile"))

        existing_email = User.query.filter(User.email == email, User.id != user.id).first()
        if existing_email:
            flash("Email already exists.", "error")
            return redirect(url_for("profile.profile"))

        email_changed = email != user.email

        user.fullname = fullname
        user.username = username
        session["username"] = username

        try:
            if email_changed:
                user.pending_email = email
                token = send_email_verification(user.id, email)
                user.email_change_token = token
                db.session.commit()
                flash("Profile updated. Please verify the new email sent to your inbox.", "success")
            else:
                db.session.commit()
                flash("Profile updated successfully.", "success")
        except Exception:
            db.session.rollback()
            flash("Could not update profile. Please try again.", "error")

        return redirect(url_for("profile.profile"))

    return render_template(
        "profile.html",
        fullname=user.fullname,
        username=user.username,
        email=user.email,
        pending_email=user.pending_email
    )

@profile_bp.route("/verify-email-change/<token>")
def verify_email_change(token):
    s = get_serializer()

    try:
        data = s.loads(token, salt="email-change-salt", max_age=3600)
    except SignatureExpired:
        flash("Verification link expired.", "error")
        return redirect(url_for("profile.profile"))
    except BadSignature:
        flash("Invalid verification link.", "error")
        return redirect(url_for("profile.profile"))

    user = User.query.get(data["user_id"])
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("auth.login"))

    if user.pending_email != data["new_email"]:
        flash("Verification no longer matches current pending email.", "error")
        return redirect(url_for("profile.profile"))

    user.email = user.pending_email
    user.pending_email = None
    user.email_change_token = None
    db.session.commit()

    flash("Email verified and updated successfully.", "success")
    return redirect(url_for("profile.profile"))

@profile_bp.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(username=session["username"]).first()

    if request.method == "POST":
        current_password = request.form["currentPassword"]
        new_password = request.form["newPassword"]
        confirm_password = request.form["confirmPassword"]

        # Validate current password
        if not user.check_password(current_password):
            flash("Current password is incorrect!", "error")
            return redirect(url_for("profile.change_password"))

        # Validate new password
        if len(new_password) < 6:
            flash("New password must be at least 6 characters long!", "error")
            return redirect(url_for("profile.change_password"))

        if new_password != confirm_password:
            flash("New password and confirmation do not match!", "error")
            return redirect(url_for("profile.change_password"))

        # Update password
        user.set_password(new_password)
        db.session.commit()

        flash("Password updated successfully!", "success")
        return redirect(url_for("profile.change_password"))

    return render_template("change-password.html")

@profile_bp.route("/delete-account", methods=["POST"])
def delete_account():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        session.pop("username", None)
        flash("User not found.", "error")
        return redirect(url_for("auth.login"))

    try:
        # SQLAlchemy cascades handle deletion of:
        # - Conversation records (via User.conversations cascade)
        # - Message records (via Conversation.messages cascade)
        db.session.delete(user)
        db.session.commit()

        # Clear the session after successful deletion
        session.clear()

        # flash("Your account has been permanently deleted.", "info")
        # ✅ Pass a flag so the login page knows to show the toast
        return redirect(url_for("auth.login") + "?deleted=true")

    except Exception as e:
        db.session.rollback()
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("profile.profile"))