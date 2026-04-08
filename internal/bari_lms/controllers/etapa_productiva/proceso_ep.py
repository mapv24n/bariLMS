
"""Etapa Productiva — Gestión relacional del proceso (momentos 1, 2, 3)."""

from flask import flash, redirect, render_template, request, url_for

from bari_lms.db import get_db
from bari_lms.middleware.auth import current_user, role_required
from bari_lms.rutas.plantillas_ep_instructor import PlantillasEPInstructor
from bari_lms.services.instructor_ep_service import InstructorEtapaProductivaService
from bari_lms.services.proceso_ep_service import ProcesoEPService


def register_routes(app):

    # ------------------------------------------------------------------
    # CU-G01 — Ver gestión del proceso EP de un aprendiz
    # ------------------------------------------------------------------

    @app.route(
        "/etapa-productiva/instructor/ficha/<ficha_id>/aprendiz/<aprendiz_id>/gestionar"
    )
    @role_required("Instructor")
    def ep_gestionar_proceso(ficha_id, aprendiz_id):
        user = current_user()
        db   = get_db()

        instructor = InstructorEtapaProductivaService.get_instructor(db, user["id"])
        if instructor is None or not InstructorEtapaProductivaService.ficha_pertenece_al_instructor(
            db, ficha_id, instructor["id"]
        ):
            flash("No tiene acceso a esta ficha.", "danger")
            return redirect(url_for("ep_instructor_fichas"))

        ficha = InstructorEtapaProductivaService.get_ficha(db, ficha_id)
        if ficha is None:
            flash("La ficha solicitada no existe.", "danger")
            return redirect(url_for("ep_instructor_fichas"))

        aprendiz_row = InstructorEtapaProductivaService.get_aprendiz_completo(
            db, ficha_id, aprendiz_id
        )
        if aprendiz_row is None:
            flash("El aprendiz no pertenece a esta ficha.", "danger")
            return redirect(url_for("ep_instructor_ficha", ficha_id=ficha_id))

        contrato  = ProcesoEPService.get_contrato(db, ficha_id, aprendiz_id)
        proceso   = ProcesoEPService.get_proceso(db, contrato["id"]) if contrato else None
        momento_1 = ProcesoEPService.get_momento_1(db, proceso["id"]) if proceso else None
        momento_2 = ProcesoEPService.get_momento_2(db, proceso["id"]) if proceso else None
        momento_3 = ProcesoEPService.get_momento_3(db, proceso["id"]) if proceso else None

        pf_id   = ficha.get("proyecto_formativo_id")
        factores = ProcesoEPService.get_factores(db, pf_id)
        eval_2  = ProcesoEPService.get_evaluaciones_m2(db, momento_2["id"]) if momento_2 else {}
        eval_3  = ProcesoEPService.get_evaluaciones_m3(db, momento_3["id"]) if momento_3 else {}

        return render_template(
            PlantillasEPInstructor.GESTIONAR,
            user=user,
            ficha=ficha,
            aprendiz=aprendiz_row,
            contrato=contrato,
            proceso=proceso,
            momento_1=momento_1,
            momento_2=momento_2,
            momento_3=momento_3,
            factores=factores,
            eval_2=eval_2,
            eval_3=eval_3,
        )

    # ------------------------------------------------------------------
    # CU-G02 — Iniciar proceso EP (POST)
    # ------------------------------------------------------------------
    # @app.route(
    #     "/etapa-productiva/instructor/ficha/<ficha_id>/aprendiz/<aprendiz_id>/gestionar/iniciar",
    #     methods=["POST"],
    # )
    # @role_required("Instructor")
    # def ep_iniciar_proceso(ficha_id, aprendiz_id):
    #      return render_template(
    #         "CONTRATO DE"
    #     )
        
    @app.route(
        "/etapa-productiva/instructor/ficha/<ficha_id>/aprendiz/<aprendiz_id>/gestionar/iniciar",
        methods=["POST"],
    )
    @role_required("Instructor")
    def ep_iniciar_proceso(ficha_id, aprendiz_id):
        user = current_user()
        db   = get_db()

        instructor = InstructorEtapaProductivaService.get_instructor(db, user["id"])
        if instructor is None or not InstructorEtapaProductivaService.ficha_pertenece_al_instructor(
            db, ficha_id, instructor["id"]
        ):
            flash("No tiene acceso a esta ficha.", "danger")
            return redirect(url_for("ep_instructor_fichas"))

        contrato = ProcesoEPService.get_contrato(db, ficha_id, aprendiz_id)
        if contrato is None:
            flash("El aprendiz no tiene un contrato activo. No se puede iniciar el proceso.", "warning")
            return redirect(url_for("ep_gestionar_proceso", ficha_id=ficha_id, aprendiz_id=aprendiz_id))

        ProcesoEPService.crear_proceso(db, contrato["id"], instructor["id"])
        flash("Proceso EP iniciado correctamente.", "success")
        return redirect(url_for("ep_gestionar_proceso", ficha_id=ficha_id, aprendiz_id=aprendiz_id))

    # ------------------------------------------------------------------
    # CU-G03 — Editar / Guardar Momento 1
    # ------------------------------------------------------------------

    @app.route("/etapa-productiva/instructor/proceso/<proceso_id>/momento-1/editar")
    @role_required("Instructor")
    def ep_editar_momento1(proceso_id):
        user = current_user()
        db   = get_db()

        ctx = _get_proceso_ctx(db, proceso_id, user["id"])
        if ctx is None:
            flash("Proceso no encontrado o sin acceso.", "danger")
            return redirect(url_for("ep_instructor_fichas"))

        return render_template(
            PlantillasEPInstructor.EDITAR_MOMENTO_1,
            user=user,
            **ctx,
            momento_1=ProcesoEPService.get_momento_1(db, proceso_id),
        )

    @app.route(
        "/etapa-productiva/instructor/proceso/<proceso_id>/momento-1/guardar",
        methods=["POST"],
    )
    @role_required("Instructor")
    def ep_guardar_momento1(proceso_id):
        user = current_user()
        db   = get_db()

        ctx = _get_proceso_ctx(db, proceso_id, user["id"])
        if ctx is None:
            flash("Proceso no encontrado o sin acceso.", "danger")
            return redirect(url_for("ep_instructor_fichas"))

        ProcesoEPService.guardar_momento_1(db, proceso_id, request.form)
        flash("Planeación guardada correctamente.", "success")
        return redirect(url_for(
            "ep_gestionar_proceso",
            ficha_id=ctx["ficha"]["id"],
            aprendiz_id=ctx["aprendiz_id"],
        ))

    # ------------------------------------------------------------------
    # CU-G04 — Editar / Guardar Momento 2
    # ------------------------------------------------------------------

    @app.route("/etapa-productiva/instructor/proceso/<proceso_id>/momento-2/editar")
    @role_required("Instructor")
    def ep_editar_momento2(proceso_id):
        user = current_user()
        db   = get_db()

        ctx = _get_proceso_ctx(db, proceso_id, user["id"])
        if ctx is None:
            flash("Proceso no encontrado o sin acceso.", "danger")
            return redirect(url_for("ep_instructor_fichas"))

        factores  = ProcesoEPService.get_factores(db, ctx["proyecto_formativo_id"])
        momento_2 = ProcesoEPService.get_momento_2(db, proceso_id)
        eval_2    = ProcesoEPService.get_evaluaciones_m2(db, momento_2["id"]) if momento_2 else {}

        return render_template(
            PlantillasEPInstructor.EDITAR_MOMENTO_2,
            user=user,
            **ctx,
            momento_2=momento_2,
            factores=factores,
            evaluaciones=eval_2,
        )

    @app.route(
        "/etapa-productiva/instructor/proceso/<proceso_id>/momento-2/guardar",
        methods=["POST"],
    )
    @role_required("Instructor")
    def ep_guardar_momento2(proceso_id):
        user = current_user()
        db   = get_db()

        ctx = _get_proceso_ctx(db, proceso_id, user["id"])
        if ctx is None:
            flash("Proceso no encontrado o sin acceso.", "danger")
            return redirect(url_for("ep_instructor_fichas"))

        factores   = ProcesoEPService.get_factores(db, ctx["proyecto_formativo_id"])
        factor_ids = [f["id"] for f in factores]

        ProcesoEPService.guardar_momento_2(db, proceso_id, request.form, factor_ids)
        flash("Seguimiento guardado correctamente.", "success")
        return redirect(url_for(
            "ep_gestionar_proceso",
            ficha_id=ctx["ficha"]["id"],
            aprendiz_id=ctx["aprendiz_id"],
        ))

    # ------------------------------------------------------------------
    # CU-G05 — Editar / Guardar Momento 3
    # ------------------------------------------------------------------

    @app.route("/etapa-productiva/instructor/proceso/<proceso_id>/momento-3/editar")
    @role_required("Instructor")
    def ep_editar_momento3(proceso_id):
        user = current_user()
        db   = get_db()

        ctx = _get_proceso_ctx(db, proceso_id, user["id"])
        if ctx is None:
            flash("Proceso no encontrado o sin acceso.", "danger")
            return redirect(url_for("ep_instructor_fichas"))

        factores  = ProcesoEPService.get_factores(db, ctx["proyecto_formativo_id"])
        momento_3 = ProcesoEPService.get_momento_3(db, proceso_id)
        eval_3    = ProcesoEPService.get_evaluaciones_m3(db, momento_3["id"]) if momento_3 else {}

        return render_template(
            PlantillasEPInstructor.EDITAR_MOMENTO_3,
            user=user,
            **ctx,
            momento_3=momento_3,
            factores=factores,
            evaluaciones=eval_3,
        )

    @app.route(
        "/etapa-productiva/instructor/proceso/<proceso_id>/momento-3/guardar",
        methods=["POST"],
    )
    @role_required("Instructor")
    def ep_guardar_momento3(proceso_id):
        user = current_user()
        db   = get_db()

        ctx = _get_proceso_ctx(db, proceso_id, user["id"])
        if ctx is None:
            flash("Proceso no encontrado o sin acceso.", "danger")
            return redirect(url_for("ep_instructor_fichas"))

        factores   = ProcesoEPService.get_factores(db, ctx["proyecto_formativo_id"])
        factor_ids = [f["id"] for f in factores]

        ProcesoEPService.guardar_momento_3(db, proceso_id, request.form, factor_ids)
        flash("Evaluación final guardada correctamente.", "success")
        return redirect(url_for(
            "ep_gestionar_proceso",
            ficha_id=ctx["ficha"]["id"],
            aprendiz_id=ctx["aprendiz_id"],
        ))


# ------------------------------------------------------------------
# Helper privado
# ------------------------------------------------------------------

def _get_proceso_ctx(db, proceso_id: str, usuario_id: str) -> dict | None:
    """Verifica acceso y devuelve contexto mínimo para las rutas de edición."""
    proceso = db.execute(
        "SELECT * FROM proceso_ep WHERE id = ?", (proceso_id,)
    ).fetchone()
    if proceso is None:
        return None

    instructor = InstructorEtapaProductivaService.get_instructor(db, usuario_id)
    if instructor is None or str(instructor["id"]) != str(proceso["instructor_id"]):
        return None

    row = db.execute(
        """
        SELECT fa.ficha_id, fa.aprendiz_id,
               f.id                    AS ficha_db_id,
               f.numero                AS ficha_numero,
               f.proyecto_formativo_id,
               p.nombre                AS programa_nombre,
               per.nombres, per.apellidos
        FROM   contrato_aprendizaje ca
        JOIN   ficha_aprendiz    fa  ON fa.id  = ca.ficha_aprendiz_id
        JOIN   ficha_formacion   f   ON f.id   = fa.ficha_id
        JOIN   programa_formacion p  ON p.id   = f.programa_formacion_id
        JOIN   aprendiz          a   ON a.id   = fa.aprendiz_id
        JOIN   persona           per ON per.id = a.persona_id
        WHERE  ca.id = ?
        """,
        (proceso["contrato_id"],),
    ).fetchone()
    if row is None:
        return None

    return {
        "proceso":               proceso,
        "ficha":                 {
            "id":              row["ficha_db_id"],
            "numero":          row["ficha_numero"],
            "programa_nombre": row["programa_nombre"],
        },
        "proyecto_formativo_id": row["proyecto_formativo_id"],
        "aprendiz_id":           row["aprendiz_id"],
        "aprendiz_nombres":      row["nombres"],
        "aprendiz_apellidos":    row["apellidos"],
    }
