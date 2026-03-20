import os
import uuid

from flask import current_app, flash, jsonify, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from bari_lms.models.repository import get_db, get_user_by_email
from bari_lms.services.auth import current_user, role_required


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

            if not check_password_hash(user_record["password_hash"], current_password):
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
                (generate_password_hash(new_password), user["id"]),
            )
            db.commit()
            flash("Contraseña actualizada correctamente.", "success")
            return redirect(url_for("instructor_change_password"))

        return render_template("instructor/change_password.html", user=user)

    @app.route("/instructor/fichas")
    @role_required("Instructor")
    def instructor_fichas():
        user = current_user()
        db = get_db()
        instructor = db.execute(
            "SELECT id FROM instructor WHERE id_usuario = ?", (user["id"],)
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
                JOIN programa_formacion p ON p.id = f.id_programa_formacion
                LEFT JOIN proyecto_formativo pf ON pf.id = f.id_proyecto_formativo
                LEFT JOIN nivel_formacion n ON n.id = p.id_nivel_formacion
                WHERE f.id_instructor = ?
                ORDER BY f.numero ASC
                """,
                (instructor["id"],),
            ).fetchall()

        return render_template("instructor/fichas.html", user=user, fichas=fichas)

    @app.route("/instructor/ficha/<int:ficha_id>/fases")
    @role_required("Instructor")
    def instructor_fases(ficha_id):
        user = current_user()
        db = get_db()
        instructor = db.execute(
            "SELECT id FROM instructor WHERE id_usuario = ?", (user["id"],)
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
            JOIN programa_formacion p ON p.id = f.id_programa_formacion
            LEFT JOIN proyecto_formativo pf ON pf.id = f.id_proyecto_formativo
            LEFT JOIN nivel_formacion n ON n.id = p.id_nivel_formacion
            WHERE f.id = ?
            """,
            (ficha_id,),
        ).fetchone()

        if ficha is None:
            flash("La ficha solicitada no existe.", "danger")
            return redirect(url_for("instructor_fichas"))

        if instructor is None or db.execute(
            "SELECT id FROM ficha_formacion WHERE id = ? AND id_instructor = ?",
            (ficha_id, instructor["id"]),
        ).fetchone() is None:
            flash("No tienes acceso a esta ficha.", "danger")
            return redirect(url_for("instructor_fichas"))

        return render_template("instructor/fases.html", user=user, ficha=ficha)

    @app.route("/api/instructor/ficha/<int:ficha_id>/tree")
    @role_required("Instructor")
    def api_instructor_ficha_tree(ficha_id):
        db = get_db()
        ficha = db.execute(
            "SELECT id_proyecto_formativo FROM ficha_formacion WHERE id = ?", (ficha_id,)
        ).fetchone()

        if ficha is None or ficha["id_proyecto_formativo"] is None:
            return jsonify({"fases": []})

        proyecto_id = ficha["id_proyecto_formativo"]
        fases = db.execute(
            "SELECT id, nombre FROM fase_proyecto WHERE id_proyecto_formativo = ? ORDER BY id ASC",
            (proyecto_id,),
        ).fetchall()

        result = []
        for fase in fases:
            acts_proy = db.execute(
                "SELECT id, nombre FROM actividad_proyecto WHERE id_fase_proyecto = ? ORDER BY id ASC",
                (fase["id"],),
            ).fetchall()

            fase_data = {"id": fase["id"], "nombre": fase["nombre"], "actividades_proyecto": []}
            for ap in acts_proy:
                guias_count = db.execute(
                    "SELECT COUNT(*) AS cnt FROM guia_actividad_proyecto WHERE id_actividad_proyecto = ?",
                    (ap["id"],),
                ).fetchone()["cnt"]

                acts_apr = db.execute(
                    """
                    SELECT aa.id, aa.nombre,
                           ga.url AS guia_url,
                           ea.id AS evidencia_id
                    FROM actividad_aprendizaje aa
                    LEFT JOIN guia_aprendizaje ga ON ga.id_actividad_aprendizaje = aa.id
                    LEFT JOIN evidencia_aprendizaje ea ON ea.id_actividad_aprendizaje = aa.id
                    WHERE aa.id_actividad_proyecto = ?
                    ORDER BY aa.id ASC
                    """,
                    (ap["id"],),
                ).fetchall()

                ap_data = {
                    "id": ap["id"],
                    "nombre": ap["nombre"],
                    "guias_count": guias_count,
                    "actividades_aprendizaje": [
                        {
                            "id": aa["id"],
                            "nombre": aa["nombre"],
                            "guia_url": aa["guia_url"],
                            "evidencia_id": aa["evidencia_id"],
                        }
                        for aa in acts_apr
                    ],
                }
                fase_data["actividades_proyecto"].append(ap_data)
            result.append(fase_data)

        return jsonify({"fases": result})

    @app.post("/api/instructor/actividad/<int:act_id>/guia")
    @role_required("Instructor")
    def api_instructor_guia_save(act_id):
        data = request.get_json() or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"ok": False, "error": "URL requerida"}), 400

        db = get_db()
        existing = db.execute(
            "SELECT id FROM guia_aprendizaje WHERE id_actividad_aprendizaje = ?", (act_id,)
        ).fetchone()

        if existing:
            db.execute(
                "UPDATE guia_aprendizaje SET url = ?, subido_en = CURRENT_TIMESTAMP WHERE id_actividad_aprendizaje = ?",
                (url, act_id),
            )
        else:
            db.execute(
                "INSERT INTO guia_aprendizaje (id_actividad_aprendizaje, url) VALUES (?, ?)",
                (act_id, url),
            )
        db.commit()
        return jsonify({"ok": True})

    @app.post("/api/instructor/actividad/<int:act_id>/evidencia")
    @role_required("Instructor")
    def api_instructor_evidencia_crear(act_id):
        data = request.get_json() or {}
        descripcion = data.get("descripcion", "").strip() or None

        db = get_db()
        existing = db.execute(
            "SELECT id FROM evidencia_aprendizaje WHERE id_actividad_aprendizaje = ?", (act_id,)
        ).fetchone()

        if existing:
            return jsonify({"ok": True, "id": existing["id"], "already_exists": True})

        row = db.execute(
            "INSERT INTO evidencia_aprendizaje (id_actividad_aprendizaje, descripcion) VALUES (?, ?) RETURNING id",
            (act_id, descripcion),
        ).fetchone()
        db.commit()
        return jsonify({"ok": True, "id": row["id"]})

    @app.route("/api/instructor/actividad/<int:act_id>/aprendices")
    @role_required("Instructor")
    def api_instructor_aprendices(act_id):
        db = get_db()
        row = db.execute(
            """
            SELECT f.id AS ficha_id, f.numero AS ficha_numero
            FROM actividad_aprendizaje aa
            JOIN actividad_proyecto ap ON ap.id = aa.id_actividad_proyecto
            JOIN fase_proyecto fp ON fp.id = ap.id_fase_proyecto
            JOIN ficha_formacion f ON f.id_proyecto_formativo = fp.id_proyecto_formativo
            WHERE aa.id = ?
            LIMIT 1
            """,
            (act_id,),
        ).fetchone()

        if row is None:
            return jsonify({"aprendices": [], "evidencia_id": None})

        evidencia = db.execute(
            "SELECT id FROM evidencia_aprendizaje WHERE id_actividad_aprendizaje = ?", (act_id,)
        ).fetchone()

        aprendices_raw = db.execute(
            """
            SELECT a.id, a.nombres, a.apellidos, a.documento,
                   u.id AS usuario_id, u.correo
            FROM aprendiz a
            LEFT JOIN usuario u ON lower(u.nombre) = lower(a.nombres || ' ' || a.apellidos)
                               AND u.rol = 'Aprendiz'
            WHERE a.ficha = ?
            ORDER BY a.nombres ASC, a.apellidos ASC
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
                    WHERE id_evidencia_aprendizaje = ? AND id_usuario = ?
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

            result.append(
                {
                    "id": ap["id"],
                    "nombre": f"{ap['nombres']} {ap['apellidos']}",
                    "documento": ap["documento"],
                    "usuario_id": ap["usuario_id"],
                    "correo": ap["correo"],
                    "entrega": entrega,
                }
            )

        return jsonify({"aprendices": result, "evidencia_id": evidencia["id"] if evidencia else None})

    @app.post("/api/instructor/entrega/<int:entrega_id>/calificar")
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

    @app.post("/api/instructor/ficha/<int:ficha_id>/fase/nueva")
    @role_required("Instructor")
    def api_instructor_fase_nueva(ficha_id):
        data = request.get_json() or {}
        nombre = data.get("nombre", "").strip()
        if not nombre:
            return jsonify({"ok": False, "error": "Nombre requerido"}), 400

        db = get_db()
        ficha = db.execute(
            "SELECT id_proyecto_formativo FROM ficha_formacion WHERE id = ?", (ficha_id,)
        ).fetchone()
        if ficha is None or ficha["id_proyecto_formativo"] is None:
            return jsonify({"ok": False, "error": "Ficha no tiene proyecto formativo"}), 400

        row = db.execute(
            "INSERT INTO fase_proyecto (id_proyecto_formativo, nombre) VALUES (?, ?) RETURNING id",
            (ficha["id_proyecto_formativo"], nombre),
        ).fetchone()
        db.commit()
        return jsonify({"ok": True, "id": row["id"], "nombre": nombre})

    @app.post("/api/instructor/fase/<int:fase_id>/actividad/nueva")
    @role_required("Instructor")
    def api_instructor_actividad_nueva(fase_id):
        data = request.get_json() or {}
        nombre = data.get("nombre", "").strip()
        if not nombre:
            return jsonify({"ok": False, "error": "Nombre requerido"}), 400

        db = get_db()
        row = db.execute(
            "INSERT INTO actividad_proyecto (id_fase_proyecto, nombre) VALUES (?, ?) RETURNING id",
            (fase_id, nombre),
        ).fetchone()
        db.commit()
        return jsonify({"ok": True, "id": row["id"], "nombre": nombre})

    @app.post("/api/instructor/actividad-proyecto/<int:act_proy_id>/aprendizaje/nueva")
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
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            upload_folder = current_app.config["UPLOAD_FOLDER_GUIAS"]
            file.save(os.path.join(upload_folder, unique_name))
            guia_url = url_for("static", filename=f"uploads/guias/{unique_name}")

        db = get_db()
        row = db.execute(
            """INSERT INTO actividad_aprendizaje
               (id_actividad_proyecto, nombre, descripcion, fecha_inicio, fecha_fin)
               VALUES (?, ?, ?, ?, ?) RETURNING id""",
            (act_proy_id, nombre, descripcion, fecha_inicio, fecha_fin),
        ).fetchone()
        aa_id = row["id"]
        if guia_url:
            db.execute(
                "INSERT INTO guia_aprendizaje (id_actividad_aprendizaje, url) VALUES (?, ?)",
                (aa_id, guia_url),
            )
        db.commit()
        return jsonify({"ok": True, "id": aa_id, "nombre": nombre})

    @app.get("/api/instructor/actividad-proyecto/<int:ap_id>/actividades-aprendizaje")
    @role_required("Instructor")
    def api_instructor_actividades_aprendizaje(ap_id):
        db = get_db()
        rows = db.execute(
            """
            SELECT aa.id, aa.nombre, aa.descripcion,
                   aa.fecha_inicio, aa.fecha_fin,
                   ga.url AS guia_url,
                   ea.id  AS evidencia_id
            FROM actividad_aprendizaje aa
            LEFT JOIN guia_aprendizaje      ga ON ga.id_actividad_aprendizaje = aa.id
            LEFT JOIN evidencia_aprendizaje ea ON ea.id_actividad_aprendizaje = aa.id
            WHERE aa.id_actividad_proyecto = ?
            ORDER BY aa.orden ASC, aa.id ASC
            """,
            (ap_id,),
        ).fetchall()

        result = []
        for r in rows:
            act = dict(r)
            secciones = db.execute(
                "SELECT id, nombre, descripcion, archivo_url, archivo_tipo, fecha_inicio, fecha_fin, orden FROM seccion_actividad WHERE id_actividad_aprendizaje=? ORDER BY orden, id",
                (act["id"],),
            ).fetchall()
            sec_list = []
            for sec in secciones:
                sub_secs = db.execute(
                    "SELECT id, nombre, descripcion, archivo_url, archivo_tipo, fecha_inicio, fecha_fin, orden FROM sub_seccion_actividad WHERE id_seccion=? ORDER BY orden, id",
                    (sec["id"],),
                ).fetchall()
                sec_list.append({**dict(sec), "sub_secciones": [dict(ss) for ss in sub_secs]})
            act["secciones"] = sec_list
            result.append(act)

        return jsonify({"actividades": result})

    @app.get("/api/instructor/actividad-proyecto/<int:ap_id>/evidencias-matriz")
    @role_required("Instructor")
    def api_instructor_evidencias_matriz(ap_id):
        db = get_db()
        ap_row = db.execute(
            """
            SELECT f.id AS ficha_id, f.numero AS ficha_numero
            FROM actividad_proyecto ap
            JOIN fase_proyecto    fp ON fp.id = ap.id_fase_proyecto
            JOIN ficha_formacion  f  ON f.id_proyecto_formativo = fp.id_proyecto_formativo
            WHERE ap.id = ?
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
            LEFT JOIN evidencia_aprendizaje ea ON ea.id_actividad_aprendizaje = aa.id
            WHERE aa.id_actividad_proyecto = ?
            ORDER BY aa.orden ASC, aa.id ASC
            """,
            (ap_id,),
        ).fetchall()

        aprendices = db.execute(
            """
            SELECT a.id, a.nombres, a.apellidos, a.documento, u.id AS usuario_id
            FROM aprendiz a
            LEFT JOIN usuario u ON lower(u.nombre) = lower(a.nombres || ' ' || a.apellidos)
                               AND u.rol = 'Aprendiz'
            WHERE a.ficha = ?
            ORDER BY a.nombres ASC, a.apellidos ASC
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
                        "WHERE id_evidencia_aprendizaje = ? AND id_usuario = ?",
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

    @app.patch("/api/instructor/actividad-proyecto/<int:ap_id>/aprendizaje/orden")
    @role_required("Instructor")
    def api_instructor_actividades_aprendizaje_orden(ap_id):
        data = request.get_json() or {}
        orden = data.get("orden", [])
        db = get_db()
        for i, aa_id in enumerate(orden):
            db.execute(
                "UPDATE actividad_aprendizaje SET orden=? WHERE id=? AND id_actividad_proyecto=?",
                (i, aa_id, ap_id),
            )
        db.commit()
        return jsonify({"ok": True})

    @app.patch("/api/instructor/actividad-aprendizaje/<int:aa_id>/secciones/orden")
    @role_required("Instructor")
    def api_instructor_secciones_orden(aa_id):
        data = request.get_json() or {}
        orden = data.get("orden", [])
        db = get_db()
        for i, sec_id in enumerate(orden):
            db.execute(
                "UPDATE seccion_actividad SET orden=? WHERE id=? AND id_actividad_aprendizaje=?",
                (i, sec_id, aa_id),
            )
        db.commit()
        return jsonify({"ok": True})

    @app.patch("/api/instructor/seccion/<int:sec_id>/sub-secciones/orden")
    @role_required("Instructor")
    def api_instructor_sub_secciones_orden(sec_id):
        data = request.get_json() or {}
        orden = data.get("orden", [])
        db = get_db()
        for i, sub_id in enumerate(orden):
            db.execute(
                "UPDATE sub_seccion_actividad SET orden=? WHERE id=? AND id_seccion=?",
                (i, sub_id, sec_id),
            )
        db.commit()
        return jsonify({"ok": True})

    @app.patch("/api/instructor/actividad-aprendizaje/<int:aa_id>/fecha-fin")
    @role_required("Instructor")
    def api_instructor_act_apr_update_fecha_fin(aa_id):
        data = request.get_json() or {}
        fecha_fin = data.get("fecha_fin", "").strip() or None
        db = get_db()
        db.execute("UPDATE actividad_aprendizaje SET fecha_fin = ? WHERE id = ?", (fecha_fin, aa_id))
        db.commit()
        return jsonify({"ok": True})

    @app.patch("/api/instructor/actividad-aprendizaje/<int:aa_id>/editar")
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
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            upload_folder = current_app.config["UPLOAD_FOLDER_GUIAS"]
            file.save(os.path.join(upload_folder, unique_name))
            guia_url = url_for("static", filename=f"uploads/guias/{unique_name}")

        db = get_db()
        db.execute(
            """UPDATE actividad_aprendizaje
               SET nombre=?, descripcion=?, fecha_inicio=?, fecha_fin=?
               WHERE id=?""",
            (nombre, descripcion, fecha_inicio, fecha_fin, aa_id),
        )
        existing_guia = db.execute(
            "SELECT id FROM guia_aprendizaje WHERE id_actividad_aprendizaje=?", (aa_id,)
        ).fetchone()

        if guia_url:
            if existing_guia:
                db.execute(
                    "UPDATE guia_aprendizaje SET url=? WHERE id_actividad_aprendizaje=?",
                    (guia_url, aa_id),
                )
            else:
                db.execute(
                    "INSERT INTO guia_aprendizaje (id_actividad_aprendizaje, url) VALUES (?, ?)",
                    (aa_id, guia_url),
                )
        else:
            if existing_guia:
                db.execute(
                    "DELETE FROM guia_aprendizaje WHERE id_actividad_aprendizaje=?", (aa_id,)
                )
        db.commit()
        return jsonify({"ok": True})

    # ── Secciones ──

    @app.post("/api/instructor/actividad-aprendizaje/<int:aa_id>/seccion/nueva")
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
        fecha_fin    = (data.get("fecha_fin")    or "").strip() or None
        db = get_db()
        row = db.execute(
            """INSERT INTO seccion_actividad
               (id_actividad_aprendizaje, nombre, descripcion, archivo_url, archivo_tipo, fecha_inicio, fecha_fin)
               VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id""",
            (aa_id, nombre, descripcion, archivo_url, archivo_tipo, fecha_inicio, fecha_fin),
        ).fetchone()
        db.commit()
        return jsonify({"ok": True, "id": row["id"]})

    @app.patch("/api/instructor/seccion/<int:sec_id>/editar")
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
        fecha_fin    = (data.get("fecha_fin")    or "").strip() or None
        db = get_db()
        db.execute(
            """UPDATE seccion_actividad
               SET nombre=?, descripcion=?, archivo_url=?, archivo_tipo=?, fecha_inicio=?, fecha_fin=?
               WHERE id=?""",
            (nombre, descripcion, archivo_url, archivo_tipo, fecha_inicio, fecha_fin, sec_id),
        )
        db.commit()
        return jsonify({"ok": True})

    @app.delete("/api/instructor/seccion/<int:sec_id>")
    @role_required("Instructor")
    def api_instructor_seccion_eliminar(sec_id):
        db = get_db()
        db.execute("DELETE FROM seccion_actividad WHERE id=?", (sec_id,))
        db.commit()
        return jsonify({"ok": True})

    # ── Sub-secciones ──

    @app.post("/api/instructor/seccion/<int:sec_id>/sub-seccion/nueva")
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
        fecha_fin    = (data.get("fecha_fin")    or "").strip() or None
        db = get_db()
        row = db.execute(
            """INSERT INTO sub_seccion_actividad
               (id_seccion, nombre, descripcion, archivo_url, archivo_tipo, fecha_inicio, fecha_fin)
               VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id""",
            (sec_id, nombre, descripcion, archivo_url, archivo_tipo, fecha_inicio, fecha_fin),
        ).fetchone()
        db.commit()
        return jsonify({"ok": True, "id": row["id"]})

    @app.patch("/api/instructor/sub-seccion/<int:sub_id>/editar")
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
        fecha_fin    = (data.get("fecha_fin")    or "").strip() or None
        db = get_db()
        db.execute(
            """UPDATE sub_seccion_actividad
               SET nombre=?, descripcion=?, archivo_url=?, archivo_tipo=?, fecha_inicio=?, fecha_fin=?
               WHERE id=?""",
            (nombre, descripcion, archivo_url, archivo_tipo, fecha_inicio, fecha_fin, sub_id),
        )
        db.commit()
        return jsonify({"ok": True})

    @app.delete("/api/instructor/sub-seccion/<int:sub_id>")
    @role_required("Instructor")
    def api_instructor_sub_seccion_eliminar(sub_id):
        db = get_db()
        db.execute("DELETE FROM sub_seccion_actividad WHERE id=?", (sub_id,))
        db.commit()
        return jsonify({"ok": True})

    # ── Guías por Actividad de Proyecto ──

    @app.get("/api/instructor/actividad-proyecto/<int:ap_id>/guias")
    @role_required("Instructor")
    def api_instructor_guias_ap(ap_id):
        db = get_db()
        rows = db.execute(
            "SELECT id, nombre, url, descripcion, orden, subido_en FROM guia_actividad_proyecto WHERE id_actividad_proyecto = ? ORDER BY orden ASC, id ASC",
            (ap_id,),
        ).fetchall()
        return jsonify({"guias": [dict(r) for r in rows]})

    @app.post("/api/instructor/actividad-proyecto/<int:ap_id>/guias/nueva")
    @role_required("Instructor")
    def api_instructor_guia_ap_nueva(ap_id):
        guia_url = None
        nombre = (request.form.get("nombre") or "").strip() or None

        if "guia_archivo" in request.files and request.files["guia_archivo"].filename:
            file = request.files["guia_archivo"]
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
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
            "INSERT INTO guia_actividad_proyecto (id_actividad_proyecto, nombre, url) VALUES (?, ?, ?) RETURNING id",
            (ap_id, nombre, guia_url),
        ).fetchone()
        db.commit()
        return jsonify({"ok": True, "id": row["id"], "nombre": nombre, "url": guia_url})

    @app.patch("/api/instructor/guia-actividad-proyecto/<int:guia_id>/editar")
    @role_required("Instructor")
    def api_instructor_guia_ap_editar(guia_id):
        data = request.get_json() or {}
        nombre = data.get("nombre", "").strip() or None
        url = data.get("url", "").strip() or None
        descripcion = data.get("descripcion", "").strip() or None
        db = get_db()
        db.execute(
            "UPDATE guia_actividad_proyecto SET nombre=?, url=COALESCE(?, url), descripcion=? WHERE id=?",
            (nombre, url, descripcion, guia_id),
        )
        db.commit()
        return jsonify({"ok": True})

    @app.patch("/api/instructor/actividad-proyecto/<int:ap_id>/guias/orden")
    @role_required("Instructor")
    def api_instructor_guias_orden(ap_id):
        data = request.get_json() or {}
        orden = data.get("orden", [])
        db = get_db()
        for i, guia_id in enumerate(orden):
            db.execute(
                "UPDATE guia_actividad_proyecto SET orden=? WHERE id=? AND id_actividad_proyecto=?",
                (i, guia_id, ap_id),
            )
        db.commit()
        return jsonify({"ok": True})

    @app.delete("/api/instructor/guia-actividad-proyecto/<int:guia_id>")
    @role_required("Instructor")
    def api_instructor_guia_ap_eliminar(guia_id):
        db = get_db()
        db.execute("DELETE FROM guia_actividad_proyecto WHERE id = ?", (guia_id,))
        db.commit()
        return jsonify({"ok": True})

    # ── Asistencia de Aprendices ──

    @app.get("/api/instructor/ficha/<int:ficha_id>/asistencia")
    @role_required("Instructor")
    def api_instructor_asistencia(ficha_id):
        fecha = request.args.get("fecha", "").strip()
        db = get_db()
        ficha = db.execute("SELECT numero FROM ficha_formacion WHERE id = ?", (ficha_id,)).fetchone()
        if ficha is None:
            return jsonify({"aprendices": [], "fecha": fecha})

        aprendices = db.execute(
            """
            SELECT a.id, a.nombres, a.apellidos, a.documento
            FROM aprendiz a
            WHERE a.ficha = ?
            ORDER BY a.nombres ASC, a.apellidos ASC
            """,
            (ficha["numero"],),
        ).fetchall()

        result = []
        for ap in aprendices:
            estado = "Presente"
            if fecha:
                row = db.execute(
                    "SELECT estado FROM asistencia_aprendiz WHERE id_ficha = ? AND id_aprendiz = ? AND fecha = ?",
                    (ficha_id, ap["id"], fecha),
                ).fetchone()
                if row:
                    estado = row["estado"]
            result.append({
                "id": ap["id"],
                "nombre": f"{ap['nombres']} {ap['apellidos']}",
                "documento": ap["documento"],
                "estado": estado,
            })

        return jsonify({"aprendices": result, "fecha": fecha})

    @app.post("/api/instructor/ficha/<int:ficha_id>/asistencia")
    @role_required("Instructor")
    def api_instructor_asistencia_guardar(ficha_id):
        data = request.get_json() or {}
        fecha = (data.get("fecha") or "").strip()
        registros = data.get("registros", [])

        if not fecha:
            return jsonify({"ok": False, "error": "Fecha requerida"}), 400

        db = get_db()
        for reg in registros:
            ap_id = reg.get("id_aprendiz")
            estado = reg.get("estado", "Presente")
            if estado not in ("Presente", "Ausente", "Excusa"):
                estado = "Presente"
            db.execute(
                """
                INSERT INTO asistencia_aprendiz (id_ficha, id_aprendiz, fecha, estado)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (id_ficha, id_aprendiz, fecha) DO UPDATE SET estado = EXCLUDED.estado
                """,
                (ficha_id, ap_id, fecha, estado),
            )
        db.commit()
        return jsonify({"ok": True})
