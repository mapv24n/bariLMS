"""Controlador de autenticación: login y logout."""

import re

from flask import flash, redirect, render_template, request, session, url_for

from bari_lms.config import ROLE_TO_SLUG
from bari_lms.middleware.auth import current_user
from bari_lms.repositories.usuario import get_user_by_email, user_has_profile
from bari_lms.services.security import verify_password

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_BAD_CREDS = "Credenciales o perfil incorrectos."


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

            if not _EMAIL_RE.match(email):
                flash("Ingresa un correo electrónico válido.", "danger")
                return render_template("login.html")

            user = get_user_by_email(email)

            if user is None:
                flash(_BAD_CREDS, "danger")
                return render_template("login.html")

            if not user["active"]:
                flash("Tu cuenta está desactivada. Contacta al administrador.", "danger")
                return render_template("login.html")

            if not user_has_profile(user["id"], role):
                flash(_BAD_CREDS, "danger")
                return render_template("login.html")

            if not verify_password(user["password_hash"], password):
                flash(_BAD_CREDS, "danger")
                return render_template("login.html")

            session.clear()
            session["user_email"] = user["email"]
            session["user_profile"] = role
            return redirect(url_for("dashboard", role_slug=ROLE_TO_SLUG[role]))

        if current_user():
            return redirect(url_for("home"))

        return render_template("login.html")

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))
