"""Etapa Productiva — sub-módulo del instructor."""

from flask import flash, redirect, render_template, url_for

from bari_lms.db import get_db
from bari_lms.middleware.auth import current_user, role_required


# ---------------------------------------------------------------------------
# Helpers de consulta
# ---------------------------------------------------------------------------

def _get_instructor(db, usuario_id):
    """Obtiene el registro instructor cuyo persona_id coincide con usuario_id.
    En el esquema PostgreSQL persona.id = usuario.id (mismo UUID).
    """
    return db.execute(
        "SELECT id FROM instructor WHERE persona_id = ?", (usuario_id,)
    ).fetchone()


def _get_fichas_ep(db, instructor_id):
    """Fichas asignadas al instructor (CU003 — listado EP)."""
    return db.execute(
        """
        SELECT f.id, f.numero,
               p.nombre  AS programa_nombre,
               pf.nombre AS proyecto_nombre,
               pf.codigo AS proyecto_codigo,
               n.nombre  AS nivel_nombre
        FROM   ficha_formacion f
        JOIN   programa_formacion   p  ON p.id  = f.programa_formacion_id
        LEFT JOIN proyecto_formativo pf ON pf.id = f.proyecto_formativo_id
        LEFT JOIN nivel_formacion    n  ON n.id  = p.nivel_formacion_id
        WHERE  f.instructor_id = ?
        ORDER  BY f.numero ASC
        """,
        (instructor_id,),
    ).fetchall()


def _get_ficha(db, ficha_id):
    return db.execute(
        """
        SELECT f.id, f.numero,
               p.nombre  AS programa_nombre,
               pf.nombre AS proyecto_nombre,
               pf.codigo AS proyecto_codigo,
               n.nombre  AS nivel_nombre
        FROM   ficha_formacion f
        JOIN   programa_formacion   p  ON p.id  = f.programa_formacion_id
        LEFT JOIN proyecto_formativo pf ON pf.id = f.proyecto_formativo_id
        LEFT JOIN nivel_formacion    n  ON n.id  = p.nivel_formacion_id
        WHERE  f.id = ?
        """,
        (ficha_id,),
    ).fetchone()


def _ficha_pertenece_al_instructor(db, ficha_id, instructor_id):
    return db.execute(
        "SELECT id FROM ficha_formacion WHERE id = ? AND instructor_id = ?",
        (ficha_id, instructor_id),
    ).fetchone() is not None


def _get_aprendices_ep(db, ficha_id):
    """Aprendices con en_etapa_productiva = TRUE para la ficha dada.

    Consulta ficha_aprendiz — la inscripción canónica que lleva el estado
    de fase de cada aprendiz. Solo aparecen los que están activamente en EP.
    """
    return db.execute(
        """
        SELECT
            fa.id                       AS inscripcion_id,
            fa.en_etapa_productiva,
            fa.etapa_productiva_concluida,
            fa.etapa_lectiva_concluida,
            fa.fecha_inicio_ep,
            fa.fecha_fin_ep,
            a.id                        AS aprendiz_id,
            per.nombres,
            per.apellidos,
            per.numero_documento,
            td.nombre                   AS tipo_documento,
            e.razon_social              AS empresa_nombre,
            e.nit                       AS empresa_nit
        FROM   ficha_aprendiz fa
        JOIN   aprendiz  a   ON a.id   = fa.aprendiz_id
        JOIN   persona   per ON per.id = a.persona_id
        LEFT JOIN tipo_documento td ON td.id = per.tipo_documento_id
        LEFT JOIN empresa        e  ON e.id  = fa.empresa_id
        WHERE  fa.ficha_id = ?
          AND  fa.en_etapa_productiva = TRUE
        ORDER  BY per.apellidos, per.nombres
        """,
        (ficha_id,),
    ).fetchall()


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

def register_routes(app):

    # CU003 — Listar fichas del instructor en EP
    @app.route("/etapa-productiva/instructor/fichas")
    @role_required("Instructor")
    def ep_instructor_fichas():
        user = current_user()
        db = get_db()

        instructor = _get_instructor(db, user["id"])
        fichas = _get_fichas_ep(db, instructor["id"]) if instructor else []

        if not fichas:
            return render_template(
                "etapa_productiva/novedades/sin_fichas.html", user=user
            )

        return render_template(
            "etapa_productiva/instructores.html", user=user, fichas=fichas
        )

    # CU004 — Seleccionar ficha y ver sus aprendices en EP
    @app.route("/etapa-productiva/instructor/ficha/<ficha_id>")
    @role_required("Instructor")
    def ep_instructor_ficha(ficha_id):
        user = current_user()
        db = get_db()

        instructor = _get_instructor(db, user["id"])

        if instructor is None or not _ficha_pertenece_al_instructor(
            db, ficha_id, instructor["id"]
        ):
            flash("No tiene acceso a esta ficha.", "danger")
            return redirect(url_for("ep_instructor_fichas"))

        ficha = _get_ficha(db, ficha_id)
        if ficha is None:
            flash("La ficha solicitada no existe.", "danger")
            return redirect(url_for("ep_instructor_fichas"))

        aprendices = _get_aprendices_ep(db, ficha_id)

        if not aprendices:
            return render_template(
                "etapa_productiva/novedades/sin_aprendices_ep.html",
                user=user,
                ficha=ficha,
            )

        return render_template(
            "etapa_productiva/ficha_detalle.html",
            user=user,
            ficha=ficha,
            aprendices=aprendices,
        )
