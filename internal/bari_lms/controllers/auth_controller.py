from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from bari_lms.config import DEFAULT_USERS, ROLE_TO_SLUG
from bari_lms.models.repository import get_user_by_email
from bari_lms.services.auth import current_user


def register_routes(app):
    @app.route("/")
    def home():
        user = current_user()
        if user:
            return redirect(url_for("dashboard", role_slug=user["dashboard_slug"]))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            role = request.form.get("role", "")
            user = get_user_by_email(email)

            if (
                user is None
                or not user["active"]
                or user["role"] != role
                or not check_password_hash(user["password_hash"], password)
            ):
                flash("Credenciales o perfil incorrectos. Usa uno de los accesos demo listados.", "danger")
                return render_template("login.html", demo_users=DEFAULT_USERS)

            session.clear()
            session["user_email"] = user["email"]
            return redirect(url_for("dashboard", role_slug=ROLE_TO_SLUG[user["role"]]))

        if current_user():
            return redirect(url_for("home"))

        return render_template("login.html", demo_users=DEFAULT_USERS)

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))
