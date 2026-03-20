"""Controlador instructor — perfil y cambio de contraseña."""

from flask import flash, redirect, render_template, request, url_for

from bari_lms.db import get_db
from bari_lms.middleware.auth import current_user, role_required
from bari_lms.repositories.usuario import get_user_by_email
from bari_lms.services.security import hash_password, verify_password


def register_routes(app):
    @app.route("/instructor/password", methods=["GET", "POST"])
    @role_required("Instructor")
    def instructor_change_password():
        user = current_user()

        if request.method == "POST":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            user_record = get_user_by_email(user["email"])
            if user_record is None:
                flash("No fue posible validar el usuario actual.", "danger")
                return redirect(url_for("instructor_change_password"))

            if not current_password or not new_password or not confirm_password:
                flash("Todos los campos son obligatorios.", "danger")
                return render_template("instructor/change_password.html", user=user)

            if not verify_password(user_record["password_hash"], current_password):
                flash("La contraseña actual es incorrecta.", "danger")
                return render_template("instructor/change_password.html", user=user)

            if new_password != confirm_password:
                flash("La nueva contraseña y su confirmación no coinciden.", "danger")
                return render_template("instructor/change_password.html", user=user)

            if len(new_password) < 8:
                flash("La nueva contraseña debe tener al menos 8 caracteres.", "danger")
                return render_template("instructor/change_password.html", user=user)

            if current_password == new_password:
                flash("La nueva contraseña debe ser diferente a la actual.", "danger")
                return render_template("instructor/change_password.html", user=user)

            db = get_db()
            db.execute(
                "UPDATE usuario SET contrasena_hash = ? WHERE id = ?",
                (hash_password(new_password), user["id"]),
            )
            db.commit()
            flash("Contraseña actualizada correctamente.", "success")
            return redirect(url_for("instructor_change_password"))

        return render_template("instructor/change_password.html", user=user)
