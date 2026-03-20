"""Controlador admin — estructura institucional (regional, centro, sede, ambiente)."""

from flask import flash, redirect, render_template, request, url_for
from psycopg.errors import UniqueViolation as IntegrityError

from bari_lms.db import get_db
from bari_lms.middleware.auth import current_user, role_required
from bari_lms.repositories._config import ENTITY_CONFIG, STRUCTURE_ENTITIES
from bari_lms.repositories.entidad import (
    delete_entity,
    entity_form_data,
    get_entity,
    insert_entity,
    update_entity,
    validate_entity_payload,
)
from bari_lms.repositories.admin.estructura import normalize_structure_context, structure_redirect_args


def register_routes(app):
    @app.route("/admin/structure")
    @role_required("Administrador")
    def admin_structure():
        return render_template(
            "admin/structure.html",
            user=current_user(),
            **normalize_structure_context(request.args),
        )

    @app.post("/admin/structure/<entity>/create")
    @role_required("Administrador")
    def admin_structure_create(entity):
        if entity not in STRUCTURE_ENTITIES:
            return redirect(url_for("admin_structure"))
        data = entity_form_data(entity, request.form)
        error = validate_entity_payload(entity, data)
        if error:
            flash(error, "danger")
            return redirect(url_for("admin_structure", **structure_redirect_args(request.form)))
        try:
            created_id = insert_entity(entity, data)
        except IntegrityError:
            get_db().rollback()
            flash(
                f"No fue posible crear {ENTITY_CONFIG[entity]['label'].lower()}. "
                "Verifica que no exista un dato duplicado.",
                "danger",
            )
            return redirect(url_for("admin_structure", **structure_redirect_args(request.form)))
        redirect_overrides = {"edit_entity": None, "edit_id": None}
        if ENTITY_CONFIG[entity]["context_key"] != ENTITY_CONFIG[entity]["parent_key"]:
            redirect_overrides[ENTITY_CONFIG[entity]["context_key"]] = created_id
        flash(f"{ENTITY_CONFIG[entity]['label']} creada correctamente.", "success")
        return redirect(
            url_for("admin_structure", **structure_redirect_args(request.form, redirect_overrides))
        )

    @app.get("/admin/structure/<entity>/<item_id>/edit")
    @role_required("Administrador")
    def admin_structure_edit(entity, item_id):
        if entity not in STRUCTURE_ENTITIES:
            return redirect(url_for("admin_structure"))
        item = get_entity(entity, item_id)
        if item is None:
            flash("El elemento solicitado no existe.", "danger")
            return redirect(url_for("admin_structure"))
        overrides = {"edit_entity": entity, "edit_id": item_id}
        if entity == "regional":
            overrides["regional_id"] = item_id
        elif entity == "centro":
            overrides["regional_id"] = item["regional_id"]
            overrides["centro_id"] = item_id
        elif entity in {"coordinacion", "sede"}:
            centro = get_entity("centro", item["centro_id"])
            overrides["regional_id"] = centro["regional_id"]
            overrides["centro_id"] = item["centro_id"]
            overrides[ENTITY_CONFIG[entity]["context_key"]] = item_id
        elif entity == "ambiente":
            sede = get_entity("sede", item["sede_id"])
            centro = get_entity("centro", sede["centro_id"])
            overrides["regional_id"] = centro["regional_id"]
            overrides["centro_id"] = centro["id"]
            overrides["sede_id"] = sede["id"]
        return redirect(url_for("admin_structure", **overrides))

    @app.post("/admin/structure/<entity>/<item_id>/update")
    @role_required("Administrador")
    def admin_structure_update(entity, item_id):
        if entity not in STRUCTURE_ENTITIES:
            return redirect(url_for("admin_structure"))
        if get_entity(entity, item_id) is None:
            flash("El elemento solicitado no existe.", "danger")
            return redirect(url_for("admin_structure"))
        data = entity_form_data(entity, request.form)
        error = validate_entity_payload(entity, data)
        if error:
            flash(error, "danger")
            return redirect(
                url_for(
                    "admin_structure",
                    **structure_redirect_args(request.form, {"edit_entity": entity, "edit_id": item_id}),
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
                    "admin_structure",
                    **structure_redirect_args(request.form, {"edit_entity": entity, "edit_id": item_id}),
                )
            )
        flash(f"{ENTITY_CONFIG[entity]['label']} actualizada correctamente.", "success")
        return redirect(
            url_for(
                "admin_structure",
                **structure_redirect_args(request.form, {"edit_entity": None, "edit_id": None}),
            )
        )

    @app.post("/admin/structure/<entity>/<item_id>/delete")
    @role_required("Administrador")
    def admin_structure_delete(entity, item_id):
        if entity not in STRUCTURE_ENTITIES:
            return redirect(url_for("admin_structure"))
        item = get_entity(entity, item_id)
        if item is None:
            flash("El elemento solicitado no existe.", "danger")
            return redirect(url_for("admin_structure"))
        redirect_args = structure_redirect_args(request.form)
        if entity == "regional" and redirect_args.get("regional_id") == item_id:
            for key in ("regional_id", "centro_id", "coordinacion_id", "sede_id"):
                redirect_args.pop(key, None)
        elif entity == "centro" and redirect_args.get("centro_id") == item_id:
            for key in ("centro_id", "coordinacion_id", "sede_id"):
                redirect_args.pop(key, None)
        elif entity == "coordinacion" and redirect_args.get("coordinacion_id") == item_id:
            redirect_args.pop("coordinacion_id", None)
        elif entity == "sede" and redirect_args.get("sede_id") == item_id:
            redirect_args.pop("sede_id", None)
        delete_entity(entity, item_id)
        flash(f"{ENTITY_CONFIG[entity]['label']} eliminada correctamente.", "success")
        return redirect(url_for("admin_structure", **redirect_args))
