"""Controlador instructor — Evidencias, entregas y calificaciones."""

import uuid

from flask import jsonify, request

from bari_lms.db import get_db
from bari_lms.middleware.auth import role_required


def register_routes(app):

    # ── Crear evidencia ───────────────────────────────────────────────────────

    @app.post("/api/instructor/actividad/<act_id>/evidencia")
    @role_required("Instructor")
    def api_instructor_evidencia_crear(act_id):
        data = request.get_json() or {}
        descripcion = data.get("descripcion", "").strip() or None

        db = get_db()
        existing = db.execute(
            "SELECT id FROM evidencia_aprendizaje WHERE actividad_aprendizaje_id = ?", (act_id,)
        ).fetchone()
        if existing:
            return jsonify({"ok": True, "id": existing["id"], "already_exists": True})

        row = db.execute(
            "INSERT INTO evidencia_aprendizaje (id, actividad_aprendizaje_id, descripcion) VALUES (?, ?, ?) RETURNING id",
            (str(uuid.uuid7()), act_id, descripcion),
        ).fetchone()
        db.commit()
        return jsonify({"ok": True, "id": row["id"]})

    # ── Aprendices y entregas ─────────────────────────────────────────────────

    @app.route("/api/instructor/actividad/<act_id>/aprendices")
    @role_required("Instructor")
    def api_instructor_aprendices(act_id):
        db = get_db()
        row = db.execute(
            """
            SELECT f.id AS ficha_id, f.numero AS ficha_numero
            FROM actividad_aprendizaje aa
            JOIN actividad_proyecto ap ON ap.id = aa.actividad_proyecto_id
            JOIN fase_proyecto fp ON fp.id = ap.fase_proyecto_id
            JOIN ficha_formacion f ON f.proyecto_formativo_id = fp.proyecto_formativo_id
            WHERE aa.id = ?
            LIMIT 1
            """,
            (act_id,),
        ).fetchone()

        if row is None:
            return jsonify({"aprendices": [], "evidencia_id": None})

        evidencia = db.execute(
            "SELECT id FROM evidencia_aprendizaje WHERE actividad_aprendizaje_id = ?", (act_id,)
        ).fetchone()

        aprendices_raw = db.execute(
            """
            SELECT a.id, pe.nombres, pe.apellidos, pe.numero_documento AS documento,
                   u.id AS usuario_id, u.correo_institucional AS correo
            FROM aprendiz a
            JOIN persona pe ON pe.id = a.persona_id
            LEFT JOIN usuario u ON u.id = a.persona_id
                               AND EXISTS (
                                   SELECT 1 FROM usuario_perfil up
                                   JOIN perfil p ON p.id = up.perfil_id
                                   WHERE up.usuario_id = u.id AND p.nombre = 'Aprendiz'
                               )
            WHERE a.ficha = ?
            ORDER BY pe.nombres ASC, pe.apellidos ASC
            """,
            (row["ficha_numero"],),
        ).fetchall()

        result = []
        for ap in aprendices_raw:
            entrega = None
            if evidencia and ap["usuario_id"]:
                entrega_row = db.execute(
                    """
                    SELECT id, url, calificacion, observaciones, entregado_en
                    FROM entrega_evidencia
                    WHERE evidencia_aprendizaje_id = ? AND usuario_id = ?
                    """,
                    (evidencia["id"], ap["usuario_id"]),
                ).fetchone()
                if entrega_row:
                    entrega = {
                        "id": entrega_row["id"],
                        "url": entrega_row["url"],
                        "calificacion": entrega_row["calificacion"],
                        "observaciones": entrega_row["observaciones"],
                        "entregado_en": entrega_row["entregado_en"],
                    }
            result.append({
                "id": ap["id"],
                "nombre": f"{ap['nombres']} {ap['apellidos']}",
                "documento": ap["documento"],
                "usuario_id": ap["usuario_id"],
                "correo": ap["correo"],
                "entrega": entrega,
            })

        return jsonify({"aprendices": result, "evidencia_id": evidencia["id"] if evidencia else None})

    # ── Calificar entrega ─────────────────────────────────────────────────────

    @app.post("/api/instructor/entrega/<entrega_id>/calificar")
    @role_required("Instructor")
    def api_instructor_calificar(entrega_id):
        data = request.get_json() or {}
        calificacion = data.get("calificacion")
        observaciones = data.get("observaciones", "").strip() or None

        if calificacion is None:
            return jsonify({"ok": False, "error": "Calificación requerida"}), 400
        try:
            calificacion = float(calificacion)
            if not (0 <= calificacion <= 100):
                raise ValueError
        except (TypeError, ValueError):
            return jsonify({"ok": False, "error": "La calificación debe ser un número entre 0 y 100"}), 400

        db = get_db()
        db.execute(
            "UPDATE entrega_evidencia SET calificacion = ?, observaciones = ? WHERE id = ?",
            (calificacion, observaciones, entrega_id),
        )
        db.commit()
        return jsonify({"ok": True, "aprobado": calificacion >= 75})

    # ── Matriz de evidencias por actividad de proyecto ────────────────────────

    @app.get("/api/instructor/actividad-proyecto/<ap_id>/evidencias-matriz")
    @role_required("Instructor")
    def api_instructor_evidencias_matriz(ap_id):
        db = get_db()
        ap_row = db.execute(
            """
            SELECT f.id AS ficha_id, f.numero AS ficha_numero
            FROM actividad_proyecto ap
            JOIN fase_proyecto fp ON fp.id = ap.fase_proyecto_id
            JOIN ficha_formacion f ON f.proyecto_formativo_id = fp.proyecto_formativo_id
            WHERE ap.id = %s
            LIMIT 1
            """,
            (ap_id,),
        ).fetchone()
        if ap_row is None:
            return jsonify({"actividades": [], "aprendices": []})

        actividades = db.execute(
            """
            SELECT aa.id, aa.nombre, ea.id AS evidencia_id
            FROM actividad_aprendizaje aa
            LEFT JOIN evidencia_aprendizaje ea ON ea.actividad_aprendizaje_id = aa.id
            WHERE aa.actividad_proyecto_id = %s
            ORDER BY aa.orden ASC, aa.id ASC
            """,
            (ap_id,),
        ).fetchall()

        aprendices = db.execute(
            """
            SELECT a.id, pe.nombres, pe.apellidos, pe.numero_documento AS documento,
                   u.id AS usuario_id
            FROM aprendiz a
            JOIN persona pe ON pe.id = a.persona_id
            LEFT JOIN usuario u ON u.id = a.persona_id
                               AND EXISTS (
                                   SELECT 1 FROM usuario_perfil up
                                   JOIN perfil p ON p.id = up.perfil_id
                                   WHERE up.usuario_id = u.id AND p.nombre = 'Aprendiz'
                               )
            WHERE a.ficha = %s
            ORDER BY pe.nombres ASC, pe.apellidos ASC
            """,
            (ap_row["ficha_numero"],),
        ).fetchall()

        result_ap = []
        for apz in aprendices:
            entregas = []
            for act in actividades:
                entrega = None
                if act["evidencia_id"] and apz["usuario_id"]:
                    row = db.execute(
                        "SELECT id, url, calificacion FROM entrega_evidencia "
                        "WHERE evidencia_aprendizaje_id = %s AND usuario_id = %s",
                        (act["evidencia_id"], apz["usuario_id"]),
                    ).fetchone()
                    if row:
                        entrega = {"id": row["id"], "url": row["url"], "calificacion": row["calificacion"]}
                entregas.append({"actividad_id": act["id"], "entrega": entrega})
            result_ap.append({
                "id": apz["id"],
                "nombre": f"{apz['nombres']} {apz['apellidos']}",
                "documento": apz["documento"],
                "usuario_id": apz["usuario_id"],
                "entregas": entregas,
            })

        return jsonify({
            "actividades": [{"id": a["id"], "nombre": a["nombre"], "evidencia_id": a["evidencia_id"]} for a in actividades],
            "aprendices": result_ap,
        })
