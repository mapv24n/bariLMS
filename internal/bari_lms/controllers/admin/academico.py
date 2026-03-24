"""Controlador admin — gestión académica (red, área, programa, ficha, fases)."""

from flask import flash, redirect, render_template, request, url_for
from psycopg.errors import UniqueViolation as IntegrityError

from bari_lms.db import get_db
from bari_lms.middleware.auth import current_user, role_required
from bari_lms.repositories._config import ACADEMIC_ENTITIES, ENTITY_CONFIG
from bari_lms.repositories.admin.academico import academic_redirect_args, normalize_academic_context
from bari_lms.repositories.entidad import (
    delete_entity,
    entity_form_data,
    get_entity,
    insert_entity,
    update_entity,
    validate_academic_payload,
)


def register_routes(app):
    @app.route("/admin/academic")
    @role_required("Administrador")
    def admin_academic():
        return render_template(
            "admin/academic.html",
            user=current_user(),
            **normalize_academic_context(request.args),
        )

    @app.post("/admin/academic/<entity>/create")
    @role_required("Administrador")
    def admin_academic_create(entity):
        if entity not in ACADEMIC_ENTITIES:
            return redirect(url_for("admin_academic"))
        data = entity_form_data(entity, request.form)
        error = validate_academic_payload(entity, data)
        if error:
            flash(error, "danger")
            return redirect(url_for("admin_academic", **academic_redirect_args(request.form)))
        try:
            created_id = insert_entity(entity, data)
        except IntegrityError:
            get_db().rollback()
            flash(
                f"No fue posible crear {ENTITY_CONFIG[entity]['label'].lower()}. "
                "Verifica que no exista un dato duplicado.",
                "danger",
            )
            return redirect(url_for("admin_academic", **academic_redirect_args(request.form)))
        redirect_args = academic_redirect_args(
            request.form,
            {ENTITY_CONFIG[entity]["context_key"]: created_id, "edit_entity": None, "edit_id": None},
        )
        flash(f"{ENTITY_CONFIG[entity]['label']} creada correctamente.", "success")
        return redirect(url_for("admin_academic", **redirect_args))

    @app.get("/admin/academic/<entity>/<item_id>/edit")
    @role_required("Administrador")
    def admin_academic_edit(entity, item_id):
        if entity not in ACADEMIC_ENTITIES:
            return redirect(url_for("admin_academic"))
        item = get_entity(entity, item_id)
        if item is None:
            flash("El elemento solicitado no existe.", "danger")
            return redirect(url_for("admin_academic"))
        overrides = {"edit_entity": entity, "edit_id": item_id}
        if entity == "red":
            overrides["red_id"] = item_id
        elif entity == "area":
            overrides["red_id"] = item["red_id"]
            overrides["area_id"] = item_id
        elif entity == "programa":
            area = get_entity("area", item["area_id"])
            overrides["red_id"] = area["red_id"]
            overrides["area_id"] = item["area_id"]
            overrides["programa_id"] = item_id
            overrides["nivel_id"] = item["nivel_id"]
        elif entity == "ficha":
            programa = get_entity("programa", item["programa_id"])
            area = get_entity("area", programa["area_id"])
            overrides["red_id"] = area["red_id"]
            overrides["area_id"] = area["id"]
            overrides["programa_id"] = programa["id"]
        elif entity == "nivel":
            overrides["nivel_id"] = item_id
        elif entity == "proyecto_formativo":
            overrides["proyecto_formativo_id"] = item_id
        elif entity == "fase_proyecto":
            overrides["proyecto_formativo_id"] = item["proyecto_formativo_id"]
            overrides["fase_id"] = item_id
        elif entity == "actividad_proyecto":
            fase = get_entity("fase_proyecto", item["fase_id"])
            overrides["proyecto_formativo_id"] = fase["proyecto_formativo_id"]
            overrides["fase_id"] = fase["id"]
            overrides["actividad_proyecto_id"] = item_id
        elif entity == "actividad_aprendizaje":
            ap = get_entity("actividad_proyecto", item["actividad_proyecto_id"])
            fase = get_entity("fase_proyecto", ap["fase_id"])
            overrides["proyecto_formativo_id"] = fase["proyecto_formativo_id"]
            overrides["fase_id"] = fase["id"]
            overrides["actividad_proyecto_id"] = ap["id"]
        return redirect(url_for("admin_academic", **overrides))

    @app.post("/admin/academic/<entity>/<item_id>/update")
    @role_required("Administrador")
    def admin_academic_update(entity, item_id):
        if entity not in ACADEMIC_ENTITIES:
            return redirect(url_for("admin_academic"))
        if get_entity(entity, item_id) is None:
            flash("El elemento solicitado no existe.", "danger")
            return redirect(url_for("admin_academic"))
        data = entity_form_data(entity, request.form)
        error = validate_academic_payload(entity, data)
        if error:
            flash(error, "danger")
            return redirect(
                url_for(
                    "admin_academic",
                    **academic_redirect_args(request.form, {"edit_entity": entity, "edit_id": item_id}),
                )
            )
        try:
            update_entity(entity, item_id, data)
        except IntegrityError:
            get_db().rollback()
            flash(
                f"No fue posible actualizar {ENTITY_CONFIG[entity]['label'].lower()}. "
                "Verifica los datos ingresados.",
                "danger",
            )
            return redirect(
                url_for(
                    "admin_academic",
                    **academic_redirect_args(request.form, {"edit_entity": entity, "edit_id": item_id}),
                )
            )
        flash(f"{ENTITY_CONFIG[entity]['label']} actualizada correctamente.", "success")
        return redirect(url_for("admin_academic", **academic_redirect_args(request.form)))

    @app.post("/admin/academic/ficha/<ficha_id>/competencia/add")
    @role_required("Administrador")
    def admin_ficha_competencia_add(ficha_id):
        ficha = get_entity("ficha", ficha_id)
        if ficha is None:
            flash("La ficha solicitada no existe.", "danger")
            return redirect(url_for("admin_academic"))
        instructor_id = request.form.get("instructor_id", "").strip()
        if not instructor_id:
            flash("Debes seleccionar un instructor.", "danger")
            return redirect(url_for("admin_academic", **academic_redirect_args(request.form)))
        db = get_db()
        try:
            import uuid as _uuid
            db.execute(
                "INSERT INTO ficha_instructor_competencia (id, ficha_id, instructor_id) "
                "VALUES (?, ?, ?) ON CONFLICT (ficha_id, instructor_id) DO NOTHING",
                (str(_uuid.uuid7()), ficha_id, instructor_id),
            )
            db.commit()
        except Exception:
            db.rollback()
            flash("No fue posible agregar el instructor a competencias.", "danger")
            return redirect(url_for("admin_academic", **academic_redirect_args(request.form)))
        flash("Instructor agregado a competencias correctamente.", "success")
        return redirect(url_for("admin_academic", **academic_redirect_args(request.form)))

    @app.post("/admin/academic/ficha/<ficha_id>/competencia/<instructor_id>/remove")
    @role_required("Administrador")
    def admin_ficha_competencia_remove(ficha_id, instructor_id):
        db = get_db()
        db.execute(
            "DELETE FROM ficha_instructor_competencia WHERE ficha_id = ? AND instructor_id = ?",
            (ficha_id, instructor_id),
        )
        db.commit()
        flash("Instructor removido de competencias.", "success")
        return redirect(url_for("admin_academic", **academic_redirect_args(request.form)))

    @app.post("/admin/academic/<entity>/<item_id>/delete")
    @role_required("Administrador")
    def admin_academic_delete(entity, item_id):
        if entity not in ACADEMIC_ENTITIES:
            return redirect(url_for("admin_academic"))
        item = get_entity(entity, item_id)
        if item is None:
            flash("El elemento solicitado no existe.", "danger")
            return redirect(url_for("admin_academic"))
        redirect_args = academic_redirect_args(request.form)
        if entity == "red" and redirect_args.get("red_id") == item_id:
            for key in ("red_id", "area_id", "programa_id"):
                redirect_args.pop(key, None)
        elif entity == "area" and redirect_args.get("area_id") == item_id:
            for key in ("area_id", "programa_id"):
                redirect_args.pop(key, None)
        elif entity == "programa" and redirect_args.get("programa_id") == item_id:
            redirect_args.pop("programa_id", None)
        elif entity == "nivel" and redirect_args.get("nivel_id") == item_id:
            redirect_args.pop("nivel_id", None)
        elif entity == "proyecto_formativo" and redirect_args.get("proyecto_formativo_id") == item_id:
            for key in ("proyecto_formativo_id", "fase_id"):
                redirect_args.pop(key, None)
        elif entity == "fase_proyecto" and redirect_args.get("fase_id") == item_id:
            for key in ("fase_id", "actividad_proyecto_id"):
                redirect_args.pop(key, None)
        elif entity == "actividad_proyecto" and redirect_args.get("actividad_proyecto_id") == item_id:
            redirect_args.pop("actividad_proyecto_id", None)
        delete_entity(entity, item_id)
        flash(f"{ENTITY_CONFIG[entity]['label']} eliminada correctamente.", "success")
        return redirect(url_for("admin_academic", **redirect_args))
