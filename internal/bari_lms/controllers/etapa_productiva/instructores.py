"""Etapa Productiva — sub-módulo del instructor."""

from flask import flash, redirect, render_template, url_for

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

        if not empresas:
            return render_template(
                PlantillasEPInstructor.SIN_EMPRESAS, user=user, ficha=ficha
            )

        return render_template(
            PlantillasEPInstructor.FICHA_DETALLE,
            user=user,
            ficha=ficha,
            aprendices=aprendices,
            empresas=empresas,
        )

