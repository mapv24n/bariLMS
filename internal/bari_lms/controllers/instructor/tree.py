"""Controlador instructor — Árbol de fases del proyecto formativo."""

from flask import jsonify

from bari_lms.db import get_db
from bari_lms.middleware.auth import role_required


def register_routes(app):

    @app.route("/api/instructor/ficha/<ficha_id>/tree")
    @role_required("Instructor")
    def api_instructor_ficha_tree(ficha_id):
        db = get_db()
        ficha = db.execute(
            "SELECT proyecto_formativo_id FROM ficha_formacion WHERE id = ?", (ficha_id,)
        ).fetchone()

        if ficha is None or ficha["proyecto_formativo_id"] is None:
            return jsonify({"fases": []})

        proyecto_id = ficha["proyecto_formativo_id"]
        fases = db.execute(
            "SELECT id, nombre FROM fase_proyecto WHERE proyecto_formativo_id = ? ORDER BY id ASC",
            (proyecto_id,),
        ).fetchall()

        result = []
        for fase in fases:
            acts_proy = db.execute(
                "SELECT id, nombre FROM actividad_proyecto WHERE fase_proyecto_id = ? ORDER BY id ASC",
                (fase["id"],),
            ).fetchall()
            fase_data = {"id": fase["id"], "nombre": fase["nombre"], "actividades_proyecto": []}
            for ap in acts_proy:
                guias_count = db.execute(
                    "SELECT COUNT(*) AS cnt FROM guia_actividad_proyecto WHERE actividad_proyecto_id = ?",
                    (ap["id"],),
                ).fetchone()["cnt"]
                acts_apr = db.execute(
                    """
                    SELECT aa.id, aa.nombre,
                           ga.url AS guia_url,
                           ea.id AS evidencia_id
                    FROM actividad_aprendizaje aa
                    LEFT JOIN guia_aprendizaje ga ON ga.actividad_aprendizaje_id = aa.id
                    LEFT JOIN evidencia_aprendizaje ea ON ea.actividad_aprendizaje_id = aa.id
                    WHERE aa.actividad_proyecto_id = ?
                    ORDER BY aa.id ASC
                    """,
                    (ap["id"],),
                ).fetchall()
                fase_data["actividades_proyecto"].append({
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
                })
            result.append(fase_data)

        return jsonify({"fases": result})
