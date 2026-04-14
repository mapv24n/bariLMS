"""Etapa Productiva — sub-módulo del instructor."""

from flask import flash, redirect, render_template, request, url_for

from bari_lms.db import get_db
from bari_lms.middleware.auth import current_user, role_required
from bari_lms.rutas.plantillas_ep_instructor import PlantillasEPInstructor
from bari_lms.services.instructor_ep_service import InstructorEtapaProductivaService


def register_routes(app):

    # CU003 — Listar fichas del instructor en EP
    @app.route("/etapa-productiva/instructor/fichas")
    @role_required("Instructor")
    def ep_instructor_fichas():
        user = current_user()
        db = get_db()

        instructor = InstructorEtapaProductivaService.get_instructor(db, user["id"])
        fichas = InstructorEtapaProductivaService.get_fichas_ep(db, instructor["id"]) if instructor else []

        if not fichas:
            return render_template(PlantillasEPInstructor.SIN_FICHAS, user=user)

        return render_template(PlantillasEPInstructor.FICHAS, user=user, fichas=fichas)

    # CU004 — Seleccionar ficha y ver sus aprendices en EP
    @app.route("/etapa-productiva/instructor/ficha/<ficha_id>")
    @role_required("Instructor")
    def ep_instructor_ficha(ficha_id):
        user = current_user()
        db = get_db()


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

        aprendices = InstructorEtapaProductivaService.get_aprendices_ep(db, ficha_id)

        if not aprendices:
            return render_template(
                PlantillasEPInstructor.SIN_APRENDICES, user=user, ficha=ficha
            )

        empresas = InstructorEtapaProductivaService.get_empresas_ep(db, ficha_id)

        return render_template(
            PlantillasEPInstructor.FICHA_DETALLE,
            user=user,
            ficha=ficha,
            aprendices=aprendices,
            empresas=empresas,
        )

    # Contrato de aprendizaje — crear (aprendiz sin contrato)
    @app.route(
        "/etapa-productiva/instructor/ficha/<ficha_id>/aprendiz/<aprendiz_id>/contrato/nuevo",
        methods=["GET", "POST"],
    )
    @role_required("Instructor")
    def ep_contrato_crear(ficha_id, aprendiz_id):
        user = current_user()
        db = get_db()

        instructor = InstructorEtapaProductivaService.get_instructor(db, user["id"])
        if instructor is None or not InstructorEtapaProductivaService.ficha_pertenece_al_instructor(
            db, ficha_id, instructor["id"]
        ):
            flash("No tiene acceso a esta ficha.", "danger")
            return redirect(url_for("ep_instructor_fichas"))

        ficha   = InstructorEtapaProductivaService.get_ficha(db, ficha_id)
        aprendiz = InstructorEtapaProductivaService.get_aprendiz_proceso(db, ficha_id, aprendiz_id)

        if ficha is None or aprendiz is None:
            flash("Aprendiz o ficha no encontrados.", "danger")
            return redirect(url_for("ep_instructor_ficha", ficha_id=ficha_id))

        if aprendiz["contrato_id"]:
            flash("El aprendiz ya tiene un contrato activo.", "warning")
            return redirect(url_for("ep_instructor_ficha", ficha_id=ficha_id))

        empresas_ficha = InstructorEtapaProductivaService.get_empresas_ep(db, ficha_id)
        empresas_dropdown = empresas_ficha or InstructorEtapaProductivaService.get_all_empresas(db)

        if request.method == "POST":
            empresa_id   = request.form.get("empresa_id")
            fecha_inicio = request.form.get("fecha_inicio") or None
            fecha_fin    = request.form.get("fecha_fin") or None

            error = None
            if not empresa_id:
                error = "Debe seleccionar una empresa."
            elif fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
                error = "La fecha de fin no puede ser anterior a la fecha de inicio."

            if error:
                flash(error, "danger")
                return render_template(
                    PlantillasEPInstructor.CONTRATO_CREAR,
                    user=user, ficha=ficha, aprendiz=aprendiz,
                    empresas_dropdown=empresas_dropdown,
                )

            InstructorEtapaProductivaService.crear_contrato(
                db, aprendiz["inscripcion_id"], empresa_id, fecha_inicio, fecha_fin, user["id"]
            )
            flash("Contrato de aprendizaje creado correctamente.", "success")
            return redirect(url_for("ep_instructor_ficha", ficha_id=ficha_id))

        return render_template(
            PlantillasEPInstructor.CONTRATO_CREAR,
            user=user, ficha=ficha, aprendiz=aprendiz,
            empresas_dropdown=empresas_dropdown,
        )

    # Contrato de aprendizaje — editar (aprendiz con contrato activo)
    @app.route(
        "/etapa-productiva/instructor/ficha/<ficha_id>/aprendiz/<aprendiz_id>/contrato/editar",
        methods=["GET", "POST"],
    )
    @role_required("Instructor")
    def ep_contrato_editar(ficha_id, aprendiz_id):
        user = current_user()
        db = get_db()

        instructor = InstructorEtapaProductivaService.get_instructor(db, user["id"])
        if instructor is None or not InstructorEtapaProductivaService.ficha_pertenece_al_instructor(
            db, ficha_id, instructor["id"]
        ):
            flash("No tiene acceso a esta ficha.", "danger")
            return redirect(url_for("ep_instructor_fichas"))

        ficha    = InstructorEtapaProductivaService.get_ficha(db, ficha_id)
        aprendiz = InstructorEtapaProductivaService.get_aprendiz_proceso(db, ficha_id, aprendiz_id)

        if ficha is None or aprendiz is None:
            flash("Aprendiz o ficha no encontrados.", "danger")
            return redirect(url_for("ep_instructor_ficha", ficha_id=ficha_id))

        if not aprendiz["contrato_id"]:
            flash("El aprendiz no tiene un contrato activo para editar.", "warning")
            return redirect(url_for("ep_instructor_ficha", ficha_id=ficha_id))

        empresas_ficha = InstructorEtapaProductivaService.get_empresas_ep(db, ficha_id)
        empresas_dropdown = empresas_ficha or InstructorEtapaProductivaService.get_all_empresas(db)

        if request.method == "POST":
            empresa_id   = request.form.get("empresa_id")
            fecha_inicio = request.form.get("fecha_inicio") or None
            fecha_fin    = request.form.get("fecha_fin") or None

            error = None
            if not empresa_id:
                error = "Debe seleccionar una empresa."
            elif fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
                error = "La fecha de fin no puede ser anterior a la fecha de inicio."

            if error:
                flash(error, "danger")
                return render_template(
                    PlantillasEPInstructor.CONTRATO_EDITAR,
                    user=user, ficha=ficha, aprendiz=aprendiz,
                    empresas_dropdown=empresas_dropdown,
                )

            InstructorEtapaProductivaService.actualizar_contrato(
                db, aprendiz["contrato_id"], empresa_id, fecha_inicio, fecha_fin
            )
            flash("Contrato de aprendizaje actualizado correctamente.", "success")
            return redirect(url_for("ep_instructor_ficha", ficha_id=ficha_id))

        return render_template(
            PlantillasEPInstructor.CONTRATO_EDITAR,
            user=user, ficha=ficha, aprendiz=aprendiz,
            empresas_dropdown=empresas_dropdown,
        )
