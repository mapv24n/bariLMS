"""Controlador instructor — vistas de fichas y fases."""

from flask import flash, redirect, render_template, url_for

from bari_lms.db import get_db
from bari_lms.middleware.auth import current_user, role_required


def register_routes(app):
    @app.route("/instructor/fichas")
    @role_required("Instructor")
    def instructor_fichas():
        user = current_user()
        db = get_db()
        instructor = db.execute(
            "SELECT id FROM instructor WHERE persona_id = ?", (user["id"],)
        ).fetchone()

        fichas = []
        if instructor:
            fichas = db.execute(
                """
                SELECT f.id, f.numero,
                       p.nombre AS programa_nombre,
                       pf.nombre AS proyecto_nombre,
                       pf.codigo AS proyecto_codigo,
                       n.nombre AS nivel_nombre
                FROM ficha_formacion f
                JOIN programa_formacion p ON p.id = f.programa_formacion_id
                LEFT JOIN proyecto_formativo pf ON pf.id = f.proyecto_formativo_id
                LEFT JOIN nivel_formacion n ON n.id = p.nivel_formacion_id
                WHERE f.instructor_id = ?
                ORDER BY f.numero ASC
                """,
                (instructor["id"],),
            ).fetchall()

        return render_template("instructor/fichas.html", user=user, fichas=fichas)

    @app.route("/instructor/ficha/<ficha_id>/fases")
    @role_required("Instructor")
    def instructor_fases(ficha_id):
        user = current_user()
        db = get_db()
        instructor = db.execute(
            "SELECT id FROM instructor WHERE persona_id = ?", (user["id"],)
        ).fetchone()

        ficha = db.execute(
            """
            SELECT f.id, f.numero,
                   p.nombre AS programa_nombre,
                   pf.nombre AS proyecto_nombre,
                   pf.codigo AS proyecto_codigo,
                   pf.id AS proyecto_id,
                   n.nombre AS nivel_nombre
            FROM ficha_formacion f
            JOIN programa_formacion p ON p.id = f.programa_formacion_id
            LEFT JOIN proyecto_formativo pf ON pf.id = f.proyecto_formativo_id
            LEFT JOIN nivel_formacion n ON n.id = p.nivel_formacion_id
            WHERE f.id = ?
            """,
            (ficha_id,),
        ).fetchone()

        if ficha is None:
            flash("La ficha solicitada no existe.", "danger")
            return redirect(url_for("instructor_fichas"))

        if instructor is None or db.execute(
            "SELECT id FROM ficha_formacion WHERE id = ? AND instructor_id = ?",
            (ficha_id, instructor["id"]),
        ).fetchone() is None:
            flash("No tienes acceso a esta ficha.", "danger")
            return redirect(url_for("instructor_fichas"))

        return render_template("instructor/fases.html", user=user, ficha=ficha)
