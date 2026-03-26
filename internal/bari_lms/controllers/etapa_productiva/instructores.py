"""Etapa Productiva — sub-módulo del instructor."""

import json

from flask import flash, redirect, render_template, url_for

from bari_lms.db import get_db
from bari_lms.middleware.auth import current_user, role_required
from bari_lms.models.aprendiz import Aprendiz
from bari_lms.rutas.plantillas_ep_instructor import PlantillasEPInstructor
from bari_lms.services.datos_seguimiento_ep import DatosSeguimientoEP
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

    # CU007 — Ver proceso de un aprendiz en EP
    @app.route("/etapa-productiva/instructor/ficha/<ficha_id>/aprendiz/<aprendiz_id>/proceso")
    @role_required("Instructor")
    def ep_instructor_aprendiz_proceso(ficha_id, aprendiz_id):
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

        if not aprendiz_row["contrato_id"]:
            flash(
                "El proceso del aprendiz en etapa productiva no ha iniciado.",
                "warning",
            )
            return redirect(url_for("ep_instructor_ficha", ficha_id=ficha_id))

        aprendiz = Aprendiz.desde_fila(aprendiz_row)

        # Datos del instructor para formularios
        instructor_info = InstructorEtapaProductivaService.get_instructor_info(
            db, instructor["id"]
        )
        instructor_nombre = (
            f"{instructor_info['nombres']} {instructor_info['apellidos']}"
            if instructor_info else user.get("nombre", "")
        )
        centro_nombre    = instructor_info["centro_nombre"]    if instructor_info else ""
        regional_nombre  = instructor_info["regional_nombre"]  if instructor_info else ""

        # Pre-llenar formulario Información General (Momento 0 / Planeación)
        form_ig = DatosSeguimientoEP.fill_informacion_general(
            aprendiz,
            instructor_nombre=instructor_nombre,
            instructor_correo=user.get("correo", ""),
            nivel=ficha["nivel_nombre"] or "",
            programa=ficha["programa_nombre"] or "",
            ficha_numero=ficha["numero"] or "",
            centro=centro_nombre,
            regional=regional_nombre,
        )
        form_ig_json = json.dumps(form_ig, ensure_ascii=False)
        form_m1_json = json.dumps(DatosSeguimientoEP.fill_momento_1(aprendiz), ensure_ascii=False)
        form_m2_json = json.dumps(DatosSeguimientoEP.fill_momento_2(), ensure_ascii=False)
        form_m3_json = json.dumps(DatosSeguimientoEP.fill_momento_3(), ensure_ascii=False)

        return render_template(
            PlantillasEPInstructor.PROCESO,
            user=user,
            ficha=ficha,
            aprendiz=aprendiz,
            
            form_ig_json=form_ig_json,
            form_m1_json=form_m1_json,
            form_m2_json=form_m2_json,
            form_m3_json=form_m3_json,
        )
