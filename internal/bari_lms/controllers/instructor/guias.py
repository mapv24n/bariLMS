"""Controlador instructor — Guías de aprendizaje y guías de actividad de proyecto."""

import os
import uuid

from flask import current_app, jsonify, request, url_for
from werkzeug.utils import secure_filename

from bari_lms.db import get_db
from bari_lms.middleware.auth import role_required


def register_routes(app):

    # ── Guías de aprendizaje (por actividad de aprendizaje) ───────────────────

    @app.post("/api/instructor/actividad/<act_id>/guia")
    @role_required("Instructor")
    def api_instructor_guia_save(act_id):
        data = request.get_json() or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"ok": False, "error": "URL requerida"}), 400

        db = get_db()
        existing = db.execute(
            "SELECT id FROM guia_aprendizaje WHERE actividad_aprendizaje_id = ?", (act_id,)
        ).fetchone()
        if existing:
            db.execute(
                "UPDATE guia_aprendizaje SET url = ?, subido_en = NOW() WHERE actividad_aprendizaje_id = ?",
                (url, act_id),
            )
        else:
            db.execute(
                "INSERT INTO guia_aprendizaje (id, actividad_aprendizaje_id, url) VALUES (?, ?, ?)",
                (str(uuid.uuid7()), act_id, url),
            )
        db.commit()
        return jsonify({"ok": True})

    # ── Guías por actividad de proyecto ───────────────────────────────────────

    @app.get("/api/instructor/actividad-proyecto/<ap_id>/guias")
    @role_required("Instructor")
    def api_instructor_guias_ap(ap_id):
        db = get_db()
        rows = db.execute(
            "SELECT id, nombre, url, descripcion, orden, subido_en "
            "FROM guia_actividad_proyecto WHERE actividad_proyecto_id = ? AND COALESCE(tipo, 'concertado') = 'concertado' ORDER BY orden ASC, id ASC",
            (ap_id,),
        ).fetchall()
        return jsonify({"guias": [dict(r) for r in rows]})

    @app.post("/api/instructor/actividad-proyecto/<ap_id>/guias/nueva")
    @role_required("Instructor")
    def api_instructor_guia_ap_nueva(ap_id):
        guia_url = None
        nombre = (request.form.get("nombre") or "").strip() or None

        if "guia_archivo" in request.files and request.files["guia_archivo"].filename:
            file = request.files["guia_archivo"]
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid7().hex}_{filename}"
            upload_folder = current_app.config["UPLOAD_FOLDER_GUIAS"]
            file.save(os.path.join(upload_folder, unique_name))
            guia_url = url_for("static", filename=f"uploads/guias/{unique_name}")
            if not nombre:
                nombre = file.filename
        else:
            guia_url = (request.form.get("guia_url") or "").strip() or None

        if not guia_url:
            return jsonify({"ok": False, "error": "Se requiere un archivo o URL"}), 400

        db = get_db()
        row = db.execute(
            "INSERT INTO guia_actividad_proyecto (id, actividad_proyecto_id, nombre, url, tipo) VALUES (?, ?, ?, ?, 'concertado') RETURNING id",
            (str(uuid.uuid7()), ap_id, nombre, guia_url),
        ).fetchone()
        db.commit()
        return jsonify({"ok": True, "id": row["id"], "nombre": nombre, "url": guia_url})

    @app.get("/api/instructor/actividad-proyecto/<ap_id>/guias-aprendizaje")
    @role_required("Instructor")
    def api_instructor_guias_aprendizaje_ap(ap_id):
        db = get_db()
        rows = db.execute(
            "SELECT id, nombre, url, descripcion, orden, subido_en "
            "FROM guia_actividad_proyecto WHERE actividad_proyecto_id = ? AND tipo = 'aprendizaje' ORDER BY orden ASC, id ASC",
            (ap_id,),
        ).fetchall()
        return jsonify({"guias": [dict(r) for r in rows]})

    @app.post("/api/instructor/actividad-proyecto/<ap_id>/guias-aprendizaje/nueva")
    @role_required("Instructor")
    def api_instructor_guia_aprendizaje_ap_nueva(ap_id):
        guia_url = None
        nombre = (request.form.get("nombre") or "").strip() or None

        if "guia_archivo" in request.files and request.files["guia_archivo"].filename:
            file = request.files["guia_archivo"]
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid7().hex}_{filename}"
            upload_folder = current_app.config["UPLOAD_FOLDER_GUIAS"]
            file.save(os.path.join(upload_folder, unique_name))
            guia_url = url_for("static", filename=f"uploads/guias/{unique_name}")
            if not nombre:
                nombre = file.filename
        else:
            guia_url = (request.form.get("guia_url") or "").strip() or None

        if not guia_url:
            return jsonify({"ok": False, "error": "Se requiere un archivo o URL"}), 400

        db = get_db()
        row = db.execute(
            "INSERT INTO guia_actividad_proyecto (id, actividad_proyecto_id, nombre, url, tipo) VALUES (?, ?, ?, ?, 'aprendizaje') RETURNING id",
            (str(uuid.uuid7()), ap_id, nombre, guia_url),
        ).fetchone()
        db.commit()
        return jsonify({"ok": True, "id": row["id"], "nombre": nombre, "url": guia_url})

    @app.patch("/api/instructor/guia-actividad-proyecto/<guia_id>/editar")
    @role_required("Instructor")
    def api_instructor_guia_ap_editar(guia_id):
        data = request.get_json() or {}
        nombre = data.get("nombre", "").strip() or None
        url = data.get("url", "").strip() or None
        descripcion = data.get("descripcion", "").strip() or None
        db = get_db()
        db.execute(
            "UPDATE guia_actividad_proyecto SET nombre = ?, url = COALESCE(?, url), descripcion = ? WHERE id = ?",
            (nombre, url, descripcion, guia_id),
        )
        db.commit()
        return jsonify({"ok": True})

    @app.patch("/api/instructor/actividad-proyecto/<ap_id>/guias/orden")
    @role_required("Instructor")
    def api_instructor_guias_orden(ap_id):
        data = request.get_json() or {}
        db = get_db()
        for i, guia_id in enumerate(data.get("orden", [])):
            db.execute(
                "UPDATE guia_actividad_proyecto SET orden = ? WHERE id = ? AND actividad_proyecto_id = ?",
                (i, guia_id, ap_id),
            )
        db.commit()
        return jsonify({"ok": True})

    @app.delete("/api/instructor/guia-actividad-proyecto/<guia_id>")
    @role_required("Instructor")
    def api_instructor_guia_ap_eliminar(guia_id):
        db = get_db()
        db.execute("DELETE FROM guia_actividad_proyecto WHERE id = ?", (guia_id,))
        db.commit()
        return jsonify({"ok": True})
