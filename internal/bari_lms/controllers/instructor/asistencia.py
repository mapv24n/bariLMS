"""Controlador instructor — Registro y consulta de asistencia."""

from flask import jsonify, request

from bari_lms.db import get_db
from bari_lms.middleware.auth import role_required


def register_routes(app):

    @app.get("/api/instructor/ficha/<ficha_id>/asistencia")
    @role_required("Instructor")
    def api_instructor_asistencia(ficha_id):
        fecha = request.args.get("fecha", "").strip()
        db = get_db()
        ficha = db.execute("SELECT numero FROM ficha_formacion WHERE id = ?", (ficha_id,)).fetchone()
        if ficha is None:
            return jsonify({"aprendices": [], "fecha": fecha})

        aprendices = db.execute(
            "SELECT a.id, pe.nombres, pe.apellidos, pe.numero_documento AS documento "
            "FROM aprendiz a JOIN persona pe ON pe.id = a.persona_id "
            "WHERE a.ficha = ? ORDER BY pe.nombres ASC, pe.apellidos ASC",
            (ficha["numero"],),
        ).fetchall()

        result = []
        for ap in aprendices:
            estado = "Presente"
            if fecha:
                row = db.execute(
                    "SELECT estado FROM asistencia_aprendiz WHERE ficha_id = ? AND aprendiz_id = ? AND fecha = ?",
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

    @app.post("/api/instructor/ficha/<ficha_id>/asistencia")
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
                INSERT INTO asistencia_aprendiz (id, ficha_id, aprendiz_id, fecha, estado)
                VALUES (gen_random_uuid(), ?, ?, ?, ?)
                ON CONFLICT (ficha_id, aprendiz_id, fecha) DO UPDATE SET estado = EXCLUDED.estado
                """,
                (ficha_id, ap_id, fecha, estado),
            )
        db.commit()
        return jsonify({"ok": True})
