from flask import flash, redirect, render_template, request, session, url_for
from psycopg2 import IntegrityError
from werkzeug.security import generate_password_hash

from bari_lms.config import AVAILABLE_ROLES
from bari_lms.models.repository import (
    ACADEMIC_ENTITIES,
    ENTITY_CONFIG,
    PEOPLE_ENTITIES,
    STRUCTURE_ENTITIES,
    academic_redirect_args,
    create_linked_person_user,
    delete_entity,
    delete_linked_person_user,
    entity_form_data,
    get_all_users,
    get_db,
    get_entities,
    get_entity,
    get_people_redirect_args,
    get_user_by_email,
    get_user_by_id,
    insert_entity,
    normalize_academic_context,
    normalize_people_context,
    normalize_structure_context,
    structure_redirect_args,
    sync_linked_person_user,
    update_entity,
    validate_academic_payload,
    validate_entity_payload,
)
from bari_lms.services.auth import current_user, role_required


def register_routes(app):
    @app.route("/admin/users")
    @role_required("Administrador")
    def admin_users():
        return render_template(
            "admin_users.html",
            user=current_user(),
            users=get_all_users(),
            roles=AVAILABLE_ROLES,
            form_data={},
            editing_user=None,
        )

    @app.post("/admin/users/create")
    @role_required("Administrador")
    def admin_users_create():
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", "").strip()
        password = request.form.get("password", "")
        active = request.form.get("active") == "on"
        form_data = {"name": name, "email": email, "role": role, "active": active}

        if not name or not email or not role or not password:
            flash("Todos los campos son obligatorios para crear el usuario.", "danger")
            return render_template("admin_users.html", user=current_user(), users=get_all_users(), roles=AVAILABLE_ROLES, form_data=form_data, editing_user=None)
        if role not in AVAILABLE_ROLES:
            flash("El rol seleccionado no es válido.", "danger")
            return redirect(url_for("admin_users"))
        if get_user_by_email(email) is not None:
            flash("Ya existe un usuario registrado con ese correo.", "danger")
            return render_template("admin_users.html", user=current_user(), users=get_all_users(), roles=AVAILABLE_ROLES, form_data=form_data, editing_user=None)

        db = get_db()
        db.execute(
            """
            INSERT INTO usuario (correo, contrasena_hash, rol, nombre, activo)
            VALUES (?, ?, ?, ?, ?)
            """,
            (email, generate_password_hash(password), role, name, active),
        )
        db.commit()
        flash("Usuario creado correctamente.", "success")
        return redirect(url_for("admin_users"))

    @app.get("/admin/users/<int:user_id>/edit")
    @role_required("Administrador")
    def admin_users_edit(user_id):
        editing_user = get_user_by_id(user_id)
        if editing_user is None:
            flash("El usuario solicitado no existe.", "danger")
            return redirect(url_for("admin_users"))
        return render_template(
            "admin_users.html",
            user=current_user(),
            users=get_all_users(),
            roles=AVAILABLE_ROLES,
            form_data={
                "name": editing_user["name"],
                "email": editing_user["email"],
                "role": editing_user["role"],
                "active": editing_user["active"],
            },
            editing_user=editing_user,
        )

    @app.post("/admin/users/<int:user_id>/update")
    @role_required("Administrador")
    def admin_users_update(user_id):
        editing_user = get_user_by_id(user_id)
        if editing_user is None:
            flash("El usuario solicitado no existe.", "danger")
            return redirect(url_for("admin_users"))

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", "").strip()
        password = request.form.get("password", "")
        active = request.form.get("active") == "on"

        if not name or not email or not role:
            flash("Nombre, correo y rol son obligatorios.", "danger")
            return redirect(url_for("admin_users_edit", user_id=user_id))
        if role not in AVAILABLE_ROLES:
            flash("El rol seleccionado no es válido.", "danger")
            return redirect(url_for("admin_users_edit", user_id=user_id))
        existing = get_user_by_email(email)
        if existing is not None and existing["id"] != user_id:
            flash("Ya existe otro usuario con ese correo.", "danger")
            return redirect(url_for("admin_users_edit", user_id=user_id))
        if current_user()["id"] == user_id and not active:
            flash("No puedes desactivar tu propia cuenta mientras la estas usando.", "danger")
            return redirect(url_for("admin_users_edit", user_id=user_id))

        db = get_db()
        if password:
            db.execute(
                """
                UPDATE usuario
                SET nombre = ?, correo = ?, rol = ?, activo = ?, contrasena_hash = ?
                WHERE id = ?
                """,
                (name, email, role, active, generate_password_hash(password), user_id),
            )
        else:
            db.execute(
                """
                UPDATE usuario
                SET nombre = ?, correo = ?, rol = ?, activo = ?
                WHERE id = ?
                """,
                (name, email, role, active, user_id),
            )
        db.commit()
        if current_user()["id"] == user_id:
            session["user_email"] = email
        flash("Usuario actualizado correctamente.", "success")
        return redirect(url_for("admin_users"))

    @app.post("/admin/users/<int:user_id>/delete")
    @role_required("Administrador")
    def admin_users_delete(user_id):
        target_user = get_user_by_id(user_id)
        if target_user is None:
            flash("El usuario solicitado no existe.", "danger")
            return redirect(url_for("admin_users"))
        if current_user()["id"] == user_id:
            flash("No puedes eliminar tu propia cuenta.", "danger")
            return redirect(url_for("admin_users"))
        db = get_db()
        db.execute("DELETE FROM usuario WHERE id = ?", (user_id,))
        db.commit()
        flash("Usuario eliminado correctamente.", "success")
        return redirect(url_for("admin_users"))

    @app.route("/admin/people")
    @role_required("Administrador")
    def admin_people():
        return render_template("admin_people.html", user=current_user(), **normalize_people_context(request.args))

    @app.post("/admin/people/<entity>/create")
    @role_required("Administrador")
    def admin_people_create(entity):
        if entity not in PEOPLE_ENTITIES:
            return redirect(url_for("admin_people"))
        data = entity_form_data(entity, request.form)
        validation_error = validate_entity_payload(entity, data)
        if validation_error:
            flash(validation_error, "danger")
            return redirect(url_for("admin_people", **get_people_redirect_args(request.form)))
        created_id = None
        try:
            created_id = insert_entity(entity, data)
            create_linked_person_user(entity, created_id, data)
        except IntegrityError:
            get_db().rollback()
            flash(f"No fue posible crear {ENTITY_CONFIG[entity]['label'].lower()}. Verifica que no exista un dato duplicado.", "danger")
            return redirect(url_for("admin_people", **get_people_redirect_args(request.form)))
        except ValueError as error:
            if created_id is not None:
                delete_entity(entity, created_id)
            flash(str(error), "danger")
            return redirect(url_for("admin_people", **get_people_redirect_args(request.form)))
        flash(f"{ENTITY_CONFIG[entity]['label']} creada correctamente con su usuario asociado.", "success")
        return redirect(url_for("admin_people"))

    @app.get("/admin/people/<entity>/<int:item_id>/edit")
    @role_required("Administrador")
    def admin_people_edit(entity, item_id):
        if entity not in PEOPLE_ENTITIES:
            return redirect(url_for("admin_people"))
        if get_entity(entity, item_id) is None:
            flash("La persona solicitada no existe.", "danger")
            return redirect(url_for("admin_people"))
        return redirect(url_for("admin_people", edit_entity=entity, edit_id=item_id))

    @app.post("/admin/people/<entity>/<int:item_id>/update")
    @role_required("Administrador")
    def admin_people_update(entity, item_id):
        if entity not in PEOPLE_ENTITIES:
            return redirect(url_for("admin_people"))
        if get_entity(entity, item_id) is None:
            flash("La persona solicitada no existe.", "danger")
            return redirect(url_for("admin_people"))
        data = entity_form_data(entity, request.form)
        validation_error = validate_entity_payload(entity, data)
        if validation_error:
            flash(validation_error, "danger")
            return redirect(url_for("admin_people", edit_entity=entity, edit_id=item_id))
        try:
            update_entity(entity, item_id, data)
            sync_linked_person_user(entity, item_id, data)
        except IntegrityError:
            get_db().rollback()
            flash(f"No fue posible actualizar {ENTITY_CONFIG[entity]['label'].lower()}. Verifica los datos ingresados.", "danger")
            return redirect(url_for("admin_people", edit_entity=entity, edit_id=item_id))
        except ValueError as error:
            flash(str(error), "danger")
            return redirect(url_for("admin_people", edit_entity=entity, edit_id=item_id))
        flash(f"{ENTITY_CONFIG[entity]['label']} actualizada correctamente.", "success")
        return redirect(url_for("admin_people"))

    @app.post("/admin/people/<entity>/<int:item_id>/delete")
    @role_required("Administrador")
    def admin_people_delete(entity, item_id):
        if entity not in PEOPLE_ENTITIES:
            return redirect(url_for("admin_people"))
        if get_entity(entity, item_id) is None:
            flash("La persona solicitada no existe.", "danger")
            return redirect(url_for("admin_people"))
        delete_linked_person_user(entity, item_id)
        delete_entity(entity, item_id)
        flash(f"{ENTITY_CONFIG[entity]['label']} eliminada correctamente.", "success")
        return redirect(url_for("admin_people"))

    @app.route("/admin/structure")
    @role_required("Administrador")
    def admin_structure():
        return render_template("admin_structure.html", user=current_user(), **normalize_structure_context(request.args))

    @app.post("/admin/structure/<entity>/create")
    @role_required("Administrador")
    def admin_structure_create(entity):
        if entity not in STRUCTURE_ENTITIES:
            return redirect(url_for("admin_structure"))
        data = entity_form_data(entity, request.form)
        validation_error = validate_entity_payload(entity, data)
        if validation_error:
            flash(validation_error, "danger")
            return redirect(url_for("admin_structure", **structure_redirect_args(request.form)))
        try:
            created_id = insert_entity(entity, data)
        except IntegrityError:
            get_db().rollback()
            flash(f"No fue posible crear {ENTITY_CONFIG[entity]['label'].lower()}. Verifica que no exista un dato duplicado.", "danger")
            return redirect(url_for("admin_structure", **structure_redirect_args(request.form)))
        redirect_overrides = {"edit_entity": None, "edit_id": None}
        if ENTITY_CONFIG[entity]["context_key"] != ENTITY_CONFIG[entity]["parent_key"]:
            redirect_overrides[ENTITY_CONFIG[entity]["context_key"]] = created_id
        flash(f"{ENTITY_CONFIG[entity]['label']} creada correctamente.", "success")
        return redirect(url_for("admin_structure", **structure_redirect_args(request.form, redirect_overrides)))

    @app.get("/admin/structure/<entity>/<int:item_id>/edit")
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

    @app.post("/admin/structure/<entity>/<int:item_id>/update")
    @role_required("Administrador")
    def admin_structure_update(entity, item_id):
        if entity not in STRUCTURE_ENTITIES:
            return redirect(url_for("admin_structure"))
        if get_entity(entity, item_id) is None:
            flash("El elemento solicitado no existe.", "danger")
            return redirect(url_for("admin_structure"))
        data = entity_form_data(entity, request.form)
        validation_error = validate_entity_payload(entity, data)
        if validation_error:
            flash(validation_error, "danger")
            return redirect(url_for("admin_structure", **structure_redirect_args(request.form, {"edit_entity": entity, "edit_id": item_id})))
        try:
            update_entity(entity, item_id, data)
        except IntegrityError:
            get_db().rollback()
            flash(f"No fue posible actualizar {ENTITY_CONFIG[entity]['label'].lower()}. Verifica los datos ingresados.", "danger")
            return redirect(url_for("admin_structure", **structure_redirect_args(request.form, {"edit_entity": entity, "edit_id": item_id})))
        flash(f"{ENTITY_CONFIG[entity]['label']} actualizada correctamente.", "success")
        return redirect(url_for("admin_structure", **structure_redirect_args(request.form, {"edit_entity": None, "edit_id": None})))

    @app.post("/admin/structure/<entity>/<int:item_id>/delete")
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
            redirect_args.pop("regional_id", None)
            redirect_args.pop("centro_id", None)
            redirect_args.pop("coordinacion_id", None)
            redirect_args.pop("sede_id", None)
        elif entity == "centro" and redirect_args.get("centro_id") == item_id:
            redirect_args.pop("centro_id", None)
            redirect_args.pop("coordinacion_id", None)
            redirect_args.pop("sede_id", None)
        elif entity == "coordinacion" and redirect_args.get("coordinacion_id") == item_id:
            redirect_args.pop("coordinacion_id", None)
        elif entity == "sede" and redirect_args.get("sede_id") == item_id:
            redirect_args.pop("sede_id", None)
        delete_entity(entity, item_id)
        flash(f"{ENTITY_CONFIG[entity]['label']} eliminada correctamente.", "success")
        return redirect(url_for("admin_structure", **redirect_args))

    @app.route("/admin/academic")
    @role_required("Administrador")
    def admin_academic():
        return render_template("admin_academic.html", user=current_user(), **normalize_academic_context(request.args))

    @app.post("/admin/academic/<entity>/create")
    @role_required("Administrador")
    def admin_academic_create(entity):
        if entity not in ACADEMIC_ENTITIES:
            return redirect(url_for("admin_academic"))
        data = entity_form_data(entity, request.form)
        validation_error = validate_academic_payload(entity, data)
        if validation_error:
            flash(validation_error, "danger")
            return redirect(url_for("admin_academic", **academic_redirect_args(request.form)))
        try:
            created_id = insert_entity(entity, data)
        except IntegrityError:
            get_db().rollback()
            flash(f"No fue posible crear {ENTITY_CONFIG[entity]['label'].lower()}. Verifica que no exista un dato duplicado.", "danger")
            return redirect(url_for("admin_academic", **academic_redirect_args(request.form)))
        redirect_args = academic_redirect_args(request.form, {ENTITY_CONFIG[entity]["context_key"]: created_id, "edit_entity": None, "edit_id": None})
        flash(f"{ENTITY_CONFIG[entity]['label']} creada correctamente.", "success")
        return redirect(url_for("admin_academic", **redirect_args))

    @app.get("/admin/academic/<entity>/<int:item_id>/edit")
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
            actividad_proyecto = get_entity("actividad_proyecto", item["actividad_proyecto_id"])
            fase = get_entity("fase_proyecto", actividad_proyecto["fase_id"])
            overrides["proyecto_formativo_id"] = fase["proyecto_formativo_id"]
            overrides["fase_id"] = fase["id"]
            overrides["actividad_proyecto_id"] = actividad_proyecto["id"]
        return redirect(url_for("admin_academic", **overrides))

    @app.post("/admin/academic/<entity>/<int:item_id>/update")
    @role_required("Administrador")
    def admin_academic_update(entity, item_id):
        if entity not in ACADEMIC_ENTITIES:
            return redirect(url_for("admin_academic"))
        if get_entity(entity, item_id) is None:
            flash("El elemento solicitado no existe.", "danger")
            return redirect(url_for("admin_academic"))
        data = entity_form_data(entity, request.form)
        validation_error = validate_academic_payload(entity, data)
        if validation_error:
            flash(validation_error, "danger")
            return redirect(url_for("admin_academic", **academic_redirect_args(request.form, {"edit_entity": entity, "edit_id": item_id})))
        try:
            update_entity(entity, item_id, data)
        except IntegrityError:
            get_db().rollback()
            flash(f"No fue posible actualizar {ENTITY_CONFIG[entity]['label'].lower()}. Verifica los datos ingresados.", "danger")
            return redirect(url_for("admin_academic", **academic_redirect_args(request.form, {"edit_entity": entity, "edit_id": item_id})))
        flash(f"{ENTITY_CONFIG[entity]['label']} actualizada correctamente.", "success")
        return redirect(url_for("admin_academic", **academic_redirect_args(request.form)))

    @app.post("/admin/academic/<entity>/<int:item_id>/delete")
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
            redirect_args.pop("red_id", None)
            redirect_args.pop("area_id", None)
            redirect_args.pop("programa_id", None)
        elif entity == "area" and redirect_args.get("area_id") == item_id:
            redirect_args.pop("area_id", None)
            redirect_args.pop("programa_id", None)
        elif entity == "programa" and redirect_args.get("programa_id") == item_id:
            redirect_args.pop("programa_id", None)
        elif entity == "nivel" and redirect_args.get("nivel_id") == item_id:
            redirect_args.pop("nivel_id", None)
        elif entity == "proyecto_formativo" and redirect_args.get("proyecto_formativo_id") == item_id:
            redirect_args.pop("proyecto_formativo_id", None)
            redirect_args.pop("fase_id", None)
        elif entity == "fase_proyecto" and redirect_args.get("fase_id") == item_id:
            redirect_args.pop("fase_id", None)
            redirect_args.pop("actividad_proyecto_id", None)
        elif entity == "actividad_proyecto" and redirect_args.get("actividad_proyecto_id") == item_id:
            redirect_args.pop("actividad_proyecto_id", None)
        delete_entity(entity, item_id)
        flash(f"{ENTITY_CONFIG[entity]['label']} eliminada correctamente.", "success")
        return redirect(url_for("admin_academic", **redirect_args))
