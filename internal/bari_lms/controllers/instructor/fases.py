"""Controlador instructor — Gestión de fases, actividades de proyecto y actividades de aprendizaje."""

import os
import uuid

from flask import current_app, jsonify, request, url_for
from werkzeug.utils import secure_filename

from bari_lms.db import get_db
from bari_lms.middleware.auth import role_required


def register_routes(app):

    # ── Fases ─────────────────────────────────────────────────────────────────

    @app.post("/api/instructor/ficha/<ficha_id>/fase/nueva")
    @role_required("Instructor")
    def api_instructor_fase_nueva(ficha_id):
        data = request.get_json() or {}
        nombre = data.get("nombre", "").strip()
        if not nombre:
            return jsonify({"ok": False, "error": "Nombre requerido"}), 400
        db = get_db()
        ficha = db.execute(
            "SELECT proyecto_formativo_id FROM ficha_formacion WHERE id = ?", (ficha_id,)
        ).fetchone()
        if ficha is None or ficha["proyecto_formativo_id"] is None:
            return jsonify({"ok": False, "error": "Ficha no tiene proyecto formativo"}), 400
        row = db.execute(
            "INSERT INTO fase_proyecto (id, proyecto_formativo_id, nombre) VALUES (?, ?, ?) RETURNING id",
            (str(uuid.uuid7()), ficha["proyecto_formativo_id"], nombre),
        ).fetchone()
        db.commit()
        return jsonify({"ok": True, "id": row["id"], "nombre": nombre})

    # ── Actividades de proyecto ───────────────────────────────────────────────

    @app.post("/api/instructor/fase/<fase_id>/actividad/nueva")
    @role_required("Instructor")
    def api_instructor_actividad_nueva(fase_id):
        data = request.get_json() or {}
        nombre = data.get("nombre", "").strip()
        if not nombre:
            return jsonify({"ok": False, "error": "Nombre requerido"}), 400
        db = get_db()
        row = db.execute(
            "INSERT INTO actividad_proyecto (id, fase_proyecto_id, nombre) VALUES (?, ?, ?) RETURNING id",
            (str(uuid.uuid7()), fase_id, nombre),
        ).fetchone()
        db.commit()
        return jsonify({"ok": True, "id": row["id"], "nombre": nombre})

    # ── Actividades de aprendizaje ────────────────────────────────────────────

    @app.post("/api/instructor/actividad-proyecto/<act_proy_id>/aprendizaje/nueva")
    @role_required("Instructor")
    def api_instructor_act_aprendizaje_nueva(act_proy_id):
        if request.is_json:
            data = request.get_json() or {}
        else:
            data = request.form

        nombre = data.get("nombre", "").strip()
        if not nombre:
            return jsonify({"ok": False, "error": "Nombre requerido"}), 400

        descripcion = (data.get("descripcion") or "").strip() or None
        fecha_inicio = (data.get("fecha_inicio") or "").strip() or None
        fecha_fin = (data.get("fecha_fin") or "").strip() or None
        guia_url = (data.get("guia_url") or "").strip() or None

        if "guia_archivo" in request.files and request.files["guia_archivo"].filename:
            file = request.files["guia_archivo"]
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid7().hex}_{filename}"
            upload_folder = current_app.config["UPLOAD_FOLDER_GUIAS"]
            file.save(os.path.join(upload_folder, unique_name))
            guia_url = url_for("static", filename=f"uploads/guias/{unique_name}")

        db = get_db()
        row = db.execute(
            "INSERT INTO actividad_aprendizaje (id, actividad_proyecto_id, nombre, descripcion, fecha_inicio, fecha_fin) "
            "VALUES (?, ?, ?, ?, ?, ?) RETURNING id",
            (str(uuid.uuid7()), act_proy_id, nombre, descripcion, fecha_inicio, fecha_fin),
        ).fetchone()
        aa_id = row["id"]
        if guia_url:
            db.execute(
                "INSERT INTO guia_aprendizaje (id, actividad_aprendizaje_id, url) VALUES (?, ?, ?)",
                (str(uuid.uuid7()), aa_id, guia_url),
            )
        db.commit()
        return jsonify({"ok": True, "id": aa_id, "nombre": nombre})

    @app.get("/api/instructor/actividad-proyecto/<ap_id>/actividades-aprendizaje")
    @role_required("Instructor")
    def api_instructor_actividades_aprendizaje(ap_id):
        db = get_db()
        rows = db.execute(
            """
            SELECT aa.id, aa.nombre, aa.descripcion, aa.fecha_inicio, aa.fecha_fin,
                   ga.url AS guia_url,
                   ea.id  AS evidencia_id
            FROM actividad_aprendizaje aa
            LEFT JOIN guia_aprendizaje ga ON ga.actividad_aprendizaje_id = aa.id
            LEFT JOIN evidencia_aprendizaje ea ON ea.actividad_aprendizaje_id = aa.id
            WHERE aa.actividad_proyecto_id = ?
            ORDER BY aa.orden ASC, aa.id ASC
            """,
            (ap_id,),
        ).fetchall()

        result = []
        for r in rows:
            act = dict(r)
            secciones = db.execute(
                "SELECT id, nombre, descripcion, archivo_url, archivo_tipo, fecha_inicio, fecha_fin, orden "
                "FROM seccion_actividad WHERE actividad_aprendizaje_id = ? ORDER BY orden, id",
                (act["id"],),
            ).fetchall()
            sec_list = []
            for sec in secciones:
                sub_secs = db.execute(
                    "SELECT id, nombre, descripcion, archivo_url, archivo_tipo, fecha_inicio, fecha_fin, orden "
                    "FROM sub_seccion_actividad WHERE seccion_id = ? ORDER BY orden, id",
                    (sec["id"],),
                ).fetchall()
                sec_list.append({**dict(sec), "sub_secciones": [dict(ss) for ss in sub_secs]})
            act["secciones"] = sec_list
            result.append(act)

        return jsonify({"actividades": result})

    @app.delete("/api/instructor/actividad-aprendizaje/<aa_id>")
    @role_required("Instructor")
    def api_instructor_act_aprendizaje_eliminar(aa_id):
        db = get_db()
        db.execute("DELETE FROM actividad_aprendizaje WHERE id = ?", (aa_id,))
        db.commit()
        return jsonify({"ok": True})

    @app.patch("/api/instructor/actividad-proyecto/<ap_id>/aprendizaje/orden")
    @role_required("Instructor")
    def api_instructor_actividades_aprendizaje_orden(ap_id):
        data = request.get_json() or {}
        db = get_db()
        for i, aa_id in enumerate(data.get("orden", [])):
            db.execute(
                "UPDATE actividad_aprendizaje SET orden = ? WHERE id = ? AND actividad_proyecto_id = ?",
                (i, aa_id, ap_id),
            )
        db.commit()
        return jsonify({"ok": True})

    @app.patch("/api/instructor/actividad-aprendizaje/<aa_id>/fecha-fin")
    @role_required("Instructor")
    def api_instructor_act_apr_update_fecha_fin(aa_id):
        data = request.get_json() or {}
        fecha_fin = data.get("fecha_fin", "").strip() or None
        db = get_db()
        db.execute("UPDATE actividad_aprendizaje SET fecha_fin = ? WHERE id = ?", (fecha_fin, aa_id))
        db.commit()
        return jsonify({"ok": True})

    @app.patch("/api/instructor/actividad-aprendizaje/<aa_id>/editar")
    @role_required("Instructor")
    def api_instructor_act_aprendizaje_editar(aa_id):
        if request.is_json:
            data = request.get_json() or {}
        else:
            data = request.form

        nombre = data.get("nombre", "").strip()
        if not nombre:
            return jsonify({"ok": False, "error": "Nombre requerido"}), 400

        descripcion = (data.get("descripcion") or "").strip() or None
        fecha_inicio = (data.get("fecha_inicio") or "").strip() or None
        fecha_fin = (data.get("fecha_fin") or "").strip() or None
        guia_url = (data.get("guia_url") or "").strip() or None

        if "guia_archivo" in request.files and request.files["guia_archivo"].filename:
            file = request.files["guia_archivo"]
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid7().hex}_{filename}"
            upload_folder = current_app.config["UPLOAD_FOLDER_GUIAS"]
            file.save(os.path.join(upload_folder, unique_name))
            guia_url = url_for("static", filename=f"uploads/guias/{unique_name}")

        db = get_db()
        db.execute(
            "UPDATE actividad_aprendizaje SET nombre = ?, descripcion = ?, fecha_inicio = ?, fecha_fin = ? WHERE id = ?",
            (nombre, descripcion, fecha_inicio, fecha_fin, aa_id),
        )
        existing_guia = db.execute(
            "SELECT id FROM guia_aprendizaje WHERE actividad_aprendizaje_id = ?", (aa_id,)
        ).fetchone()
        if guia_url:
            if existing_guia:
                db.execute(
                    "UPDATE guia_aprendizaje SET url = ? WHERE actividad_aprendizaje_id = ?",
                    (guia_url, aa_id),
                )
            else:
                db.execute(
                    "INSERT INTO guia_aprendizaje (id, actividad_aprendizaje_id, url) VALUES (?, ?, ?)",
                    (str(uuid.uuid7()), aa_id, guia_url),
                )
        elif existing_guia:
            db.execute("DELETE FROM guia_aprendizaje WHERE actividad_aprendizaje_id = ?", (aa_id,))
        db.commit()
        return jsonify({"ok": True})
