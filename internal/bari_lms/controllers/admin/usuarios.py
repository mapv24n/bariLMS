"""Controlador admin — gestión de usuarios."""

import uuid

from flask import flash, redirect, render_template, request, session, url_for
from psycopg.errors import UniqueViolation as IntegrityError

from bari_lms.config import AVAILABLE_ROLES
from bari_lms.db import get_db
from bari_lms.middleware.auth import current_user, role_required
from bari_lms.repositories.usuario import get_all_users, get_user_by_email, get_user_by_id
from bari_lms.services.security import hash_password


def register_routes(app):
    @app.route("/admin/users")
    @role_required("Administrador")
    def admin_users():
        return render_template(
            "admin/users.html",
            user=current_user(),
            users=get_all_users(),
            roles=AVAILABLE_ROLES,
            form_data={},
            editing_user=None,
        )

    @app.post("/admin/users/create")
    @role_required("Administrador")
    def admin_users_create():
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", "").strip()
        password = request.form.get("password", "")
        active = request.form.get("active") == "on"
        form_data = {"name": name, "email": email, "role": role, "active": active}

        if not name or not email or not role or not password:
            flash("Todos los campos son obligatorios para crear el usuario.", "danger")
            return render_template(
                "admin/users.html",
                user=current_user(),
                users=get_all_users(),
                roles=AVAILABLE_ROLES,
                form_data=form_data,
                editing_user=None,
            )
        if role not in AVAILABLE_ROLES:
            flash("El rol seleccionado no es válido.", "danger")
            return redirect(url_for("admin_users"))

        db = get_db()
        user_id = str(uuid.uuid7())
        try:
            db.execute(
                "INSERT INTO usuario (id, correo_institucional, contrasena_hash, activo) VALUES (?, ?, ?, ?)",
                (user_id, email, hash_password(password), active),
            )
            db.execute(
                """
                INSERT INTO usuario_perfil (id, usuario_id, perfil_id)
                SELECT ?, ?, p.id FROM perfil p WHERE p.nombre = ?
                ON CONFLICT (usuario_id, perfil_id) DO NOTHING
                """,
                (str(uuid.uuid7()), user_id, role),
            )
            db.commit()
        except IntegrityError:
            db.rollback()
            flash("Ya existe un usuario registrado con ese correo.", "danger")
            return render_template(
                "admin/users.html",
                user=current_user(),
                users=get_all_users(),
                roles=AVAILABLE_ROLES,
                form_data=form_data,
                editing_user=None,
            )
        flash("Usuario creado correctamente.", "success")
        return redirect(url_for("admin_users"))

    @app.get("/admin/users/<user_id>/edit")
    @role_required("Administrador")
    def admin_users_edit(user_id):
        editing_user = get_user_by_id(user_id)
        if editing_user is None:
            flash("El usuario solicitado no existe.", "danger")
            return redirect(url_for("admin_users"))
        return render_template(
            "admin/users.html",
            user=current_user(),
            users=get_all_users(),
            roles=AVAILABLE_ROLES,
            form_data={
                "name": editing_user["name"],
                "email": editing_user["email"],
                "role": editing_user["role"],
                "active": editing_user["active"],
            },
            editing_user=editing_user,
        )

    @app.post("/admin/users/<user_id>/update")
    @role_required("Administrador")
    def admin_users_update(user_id):
        editing_user = get_user_by_id(user_id)
        if editing_user is None:
            flash("El usuario solicitado no existe.", "danger")
            return redirect(url_for("admin_users"))

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", "").strip()
        password = request.form.get("password", "")
        active = request.form.get("active") == "on"

        if not name or not email or not role:
            flash("Nombre, correo y rol son obligatorios.", "danger")
            return redirect(url_for("admin_users_edit", user_id=user_id))
        if role not in AVAILABLE_ROLES:
            flash("El rol seleccionado no es válido.", "danger")
            return redirect(url_for("admin_users_edit", user_id=user_id))
        existing = get_user_by_email(email)
        if existing is not None and existing["id"] != user_id:
            flash("Ya existe otro usuario con ese correo.", "danger")
            return redirect(url_for("admin_users_edit", user_id=user_id))
        if current_user()["id"] == user_id and not active:
            flash("No puedes desactivar tu propia cuenta mientras la usas.", "danger")
            return redirect(url_for("admin_users_edit", user_id=user_id))

        db = get_db()
        if password:
            db.execute(
                "UPDATE usuario SET correo_institucional = ?, activo = ?, contrasena_hash = ? WHERE id = ?",
                (email, active, hash_password(password), user_id),
            )
        else:
            db.execute(
                "UPDATE usuario SET correo_institucional = ?, activo = ? WHERE id = ?",
                (email, active, user_id),
            )
        db.execute("DELETE FROM usuario_perfil WHERE usuario_id = ?", (user_id,))
        db.execute(
            """
            INSERT INTO usuario_perfil (id, usuario_id, perfil_id)
            SELECT ?, ?, p.id FROM perfil p WHERE p.nombre = ?
            ON CONFLICT (usuario_id, perfil_id) DO NOTHING
            """,
            (str(uuid.uuid7()), user_id, role),
        )
        db.commit()
        flash("Usuario actualizado correctamente.", "success")
        return redirect(url_for("admin_users"))

    @app.post("/admin/users/<user_id>/delete")
    @role_required("Administrador")
    def admin_users_delete(user_id):
        target_user = get_user_by_id(user_id)
        if target_user is None:
            flash("El usuario solicitado no existe.", "danger")
            return redirect(url_for("admin_users"))
        if current_user()["id"] == user_id:
            flash("No puedes eliminar tu propia cuenta.", "danger")
            return redirect(url_for("admin_users"))
        db = get_db()
        db.execute("DELETE FROM usuario WHERE id = ?", (user_id,))
        db.commit()
        flash("Usuario eliminado correctamente.", "success")
        return redirect(url_for("admin_users"))
