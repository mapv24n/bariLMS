"""Controlador instructor — Secciones y sub-secciones de actividades de aprendizaje."""

import uuid

from flask import jsonify, request

from bari_lms.db import get_db
from bari_lms.middleware.auth import role_required


def register_routes(app):

    # ── Orden ─────────────────────────────────────────────────────────────────

    @app.patch("/api/instructor/actividad-aprendizaje/<aa_id>/secciones/orden")
    @role_required("Instructor")
    def api_instructor_secciones_orden(aa_id):
        data = request.get_json() or {}
        db = get_db()
        for i, sec_id in enumerate(data.get("orden", [])):
            db.execute(
                "UPDATE seccion_actividad SET orden = ? WHERE id = ? AND actividad_aprendizaje_id = ?",
                (i, sec_id, aa_id),
            )
        db.commit()
        return jsonify({"ok": True})

    @app.patch("/api/instructor/seccion/<sec_id>/sub-secciones/orden")
    @role_required("Instructor")
    def api_instructor_sub_secciones_orden(sec_id):
        data = request.get_json() or {}
        db = get_db()
        for i, sub_id in enumerate(data.get("orden", [])):
            db.execute(
                "UPDATE sub_seccion_actividad SET orden = ? WHERE id = ? AND seccion_id = ?",
                (i, sub_id, sec_id),
            )
        db.commit()
        return jsonify({"ok": True})

    # ── Secciones ─────────────────────────────────────────────────────────────

    @app.post("/api/instructor/actividad-aprendizaje/<aa_id>/seccion/nueva")
    @role_required("Instructor")
    def api_instructor_seccion_nueva(aa_id):
        data = request.get_json() or {}
        nombre = (data.get("nombre") or "").strip()
        if not nombre:
            return jsonify({"ok": False, "error": "Nombre requerido"}), 400
        descripcion = (data.get("descripcion") or "").strip() or None
        archivo_url = (data.get("archivo_url") or "").strip() or None
        archivo_tipo = (data.get("archivo_tipo") or "").strip() or None
        fecha_inicio = (data.get("fecha_inicio") or "").strip() or None
        fecha_fin = (data.get("fecha_fin") or "").strip() or None
        db = get_db()
        row = db.execute(
            "INSERT INTO seccion_actividad "
            "(id, actividad_aprendizaje_id, nombre, descripcion, archivo_url, archivo_tipo, fecha_inicio, fecha_fin) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?) RETURNING id",
            (str(uuid.uuid7()), aa_id, nombre, descripcion, archivo_url, archivo_tipo, fecha_inicio, fecha_fin),
        ).fetchone()
        db.commit()
        return jsonify({"ok": True, "id": row["id"]})

    @app.patch("/api/instructor/seccion/<sec_id>/editar")
    @role_required("Instructor")
    def api_instructor_seccion_editar(sec_id):
        data = request.get_json() or {}
        nombre = (data.get("nombre") or "").strip()
        if not nombre:
            return jsonify({"ok": False, "error": "Nombre requerido"}), 400
        descripcion = (data.get("descripcion") or "").strip() or None
        archivo_url = (data.get("archivo_url") or "").strip() or None
        archivo_tipo = (data.get("archivo_tipo") or "").strip() or None
        fecha_inicio = (data.get("fecha_inicio") or "").strip() or None
        fecha_fin = (data.get("fecha_fin") or "").strip() or None
        db = get_db()
        db.execute(
            "UPDATE seccion_actividad SET nombre = ?, descripcion = ?, archivo_url = ?, "
            "archivo_tipo = ?, fecha_inicio = ?, fecha_fin = ? WHERE id = ?",
            (nombre, descripcion, archivo_url, archivo_tipo, fecha_inicio, fecha_fin, sec_id),
        )
        db.commit()
        return jsonify({"ok": True})

    @app.delete("/api/instructor/seccion/<sec_id>")
    @role_required("Instructor")
    def api_instructor_seccion_eliminar(sec_id):
        db = get_db()
        db.execute("DELETE FROM seccion_actividad WHERE id = ?", (sec_id,))
        db.commit()
        return jsonify({"ok": True})

    # ── Sub-secciones ─────────────────────────────────────────────────────────

    @app.post("/api/instructor/seccion/<sec_id>/sub-seccion/nueva")
    @role_required("Instructor")
    def api_instructor_sub_seccion_nueva(sec_id):
        data = request.get_json() or {}
        nombre = (data.get("nombre") or "").strip()
        if not nombre:
            return jsonify({"ok": False, "error": "Nombre requerido"}), 400
        descripcion = (data.get("descripcion") or "").strip() or None
        archivo_url = (data.get("archivo_url") or "").strip() or None
        archivo_tipo = (data.get("archivo_tipo") or "").strip() or None
        fecha_inicio = (data.get("fecha_inicio") or "").strip() or None
        fecha_fin = (data.get("fecha_fin") or "").strip() or None
        db = get_db()
        row = db.execute(
            "INSERT INTO sub_seccion_actividad "
            "(id, seccion_id, nombre, descripcion, archivo_url, archivo_tipo, fecha_inicio, fecha_fin) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?) RETURNING id",
            (str(uuid.uuid7()), sec_id, nombre, descripcion, archivo_url, archivo_tipo, fecha_inicio, fecha_fin),
        ).fetchone()
        db.commit()
        return jsonify({"ok": True, "id": row["id"]})

    @app.patch("/api/instructor/sub-seccion/<sub_id>/editar")
    @role_required("Instructor")
    def api_instructor_sub_seccion_editar(sub_id):
        data = request.get_json() or {}
        nombre = (data.get("nombre") or "").strip()
        if not nombre:
            return jsonify({"ok": False, "error": "Nombre requerido"}), 400
        descripcion = (data.get("descripcion") or "").strip() or None
        archivo_url = (data.get("archivo_url") or "").strip() or None
        archivo_tipo = (data.get("archivo_tipo") or "").strip() or None
        fecha_inicio = (data.get("fecha_inicio") or "").strip() or None
        fecha_fin = (data.get("fecha_fin") or "").strip() or None
        db = get_db()
        db.execute(
            "UPDATE sub_seccion_actividad SET nombre = ?, descripcion = ?, archivo_url = ?, "
            "archivo_tipo = ?, fecha_inicio = ?, fecha_fin = ? WHERE id = ?",
            (nombre, descripcion, archivo_url, archivo_tipo, fecha_inicio, fecha_fin, sub_id),
        )
        db.commit()
        return jsonify({"ok": True})

    @app.delete("/api/instructor/sub-seccion/<sub_id>")
    @role_required("Instructor")
    def api_instructor_sub_seccion_eliminar(sub_id):
        db = get_db()
        db.execute("DELETE FROM sub_seccion_actividad WHERE id = ?", (sub_id,))
        db.commit()
        return jsonify({"ok": True})
