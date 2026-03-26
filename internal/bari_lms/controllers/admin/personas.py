"""Controlador admin — gestión de personas (instructor, aprendiz, administrativo)."""

import csv
import io

from flask import flash, redirect, render_template, request, url_for
from psycopg.errors import UniqueViolation as IntegrityError

from bari_lms.db import get_db
from bari_lms.middleware.auth import current_user, role_required
from bari_lms.repositories._config import ENTITY_CONFIG, PEOPLE_ENTITIES
from bari_lms.repositories.entidad import (
    delete_entity,
    entity_form_data,
    update_entity,
    validate_entity_payload,
)
from bari_lms.repositories.admin.personas import (
    create_linked_person_user,
    delete_linked_person_user,
    get_people_redirect_args,
    normalize_people_context,
    sync_linked_person_user,
)

# ── Importación CSV ──────────────────────────────────────────────────────────

_IMPORT_FIELD_MAP = {
    "instructor": {"email": "correo"},
    "aprendiz": {},
    "administrativo_persona": {},
}


def _normalize_import_row(entity, row):
    mapped = {}
    field_map = _IMPORT_FIELD_MAP.get(entity, {})
    for key, value in row.items():
        normalized_key = (key or "").strip().lower()
        if not normalized_key:
            continue
        target_key = field_map.get(normalized_key, normalized_key)
        mapped[target_key] = (value or "").strip()
    config = ENTITY_CONFIG[entity]
    all_fields = config["fields"] + config.get("persona_form_fields", [])
    data = {}
    for field in all_fields:
        raw_value = mapped.get(field, "")
        if field.endswith("_id"):
            data[field] = raw_value or None
        else:
            data[field] = raw_value
    return data


def _import_people_csv(entity, storage):
    if storage is None or not storage.filename:
        return 0, ["Debes seleccionar un archivo CSV."]
    try:
        content = storage.stream.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        return 0, ["El archivo debe estar codificado en UTF-8."]

    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames:
        return 0, ["El archivo CSV no contiene encabezados."]

    created = 0
    errors = []
    for index, row in enumerate(reader, start=2):
        if not any((value or "").strip() for value in row.values()):
            continue
        try:
            data = _normalize_import_row(entity, row)
        except ValueError:
            errors.append(f"Fila {index}: uno de los identificadores es inválido.")
            continue
        error = validate_entity_payload(entity, data)
        if error:
            errors.append(f"Fila {index}: {error}")
            continue
        try:
            create_linked_person_user(entity, data)
            created += 1
        except IntegrityError:
            get_db().rollback()
            errors.append(
                f"Fila {index}: no fue posible crear el registro por datos duplicados."
            )
        except ValueError as exc:
            get_db().rollback()
            errors.append(f"Fila {index}: {exc}")

    return created, errors


# ── Rutas ────────────────────────────────────────────────────────────────────

def register_routes(app):
    @app.route("/admin/people")
    @role_required("Administrador")
    def admin_people():
        return render_template(
            "admin/people.html",
            user=current_user(),
            **normalize_people_context(request.args),
        )

    @app.post("/admin/people/<entity>/create")
    @role_required("Administrador")
    def admin_people_create(entity):
        if entity not in PEOPLE_ENTITIES:
            return redirect(url_for("admin_people"))
        data = entity_form_data(entity, request.form)
        error = validate_entity_payload(entity, data)
        if error:
            flash(error, "danger")
            return redirect(url_for("admin_people", **get_people_redirect_args(request.form)))
        try:
            create_linked_person_user(entity, data)
        except IntegrityError:
            get_db().rollback()
            flash(
                f"No fue posible crear {ENTITY_CONFIG[entity]['label'].lower()}. "
                "Verifica que no exista un dato duplicado.",
                "danger",
            )
            return redirect(url_for("admin_people", **get_people_redirect_args(request.form)))
        except ValueError as exc:
            get_db().rollback()
            flash(str(exc), "danger")
            return redirect(url_for("admin_people", **get_people_redirect_args(request.form)))
        flash(
            f"{ENTITY_CONFIG[entity]['label']} creada correctamente con su usuario asociado.",
            "success",
        )
        return redirect(url_for("admin_people"))

    @app.post("/admin/people/<entity>/import")
    @role_required("Administrador")
    def admin_people_import(entity):
        if entity not in PEOPLE_ENTITIES:
            return redirect(url_for("admin_people"))
        created, errors = _import_people_csv(entity, request.files.get("csv_file"))
        if created:
            flash(
                f"Se cargaron {created} registros de {ENTITY_CONFIG[entity]['label'].lower()}.",
                "success",
            )
        if errors:
            flash(" | ".join(errors[:5]), "warning")
            if len(errors) > 5:
                flash(f"Se omitieron {len(errors) - 5} errores adicionales.", "warning")
        if not created and not errors:
            flash("El archivo no contenía registros para importar.", "warning")
        return redirect(url_for("admin_people"))

    @app.get("/admin/people/<entity>/<item_id>/edit")
    @role_required("Administrador")
    def admin_people_edit(entity, item_id):
        if entity not in PEOPLE_ENTITIES:
            return redirect(url_for("admin_people"))
        from bari_lms.repositories.entidad import get_entity
        if get_entity(entity, item_id) is None:
            flash("La persona solicitada no existe.", "danger")
            return redirect(url_for("admin_people"))
        return redirect(url_for("admin_people", edit_entity=entity, edit_id=item_id))

    @app.post("/admin/people/<entity>/<item_id>/update")
    @role_required("Administrador")
    def admin_people_update(entity, item_id):
        if entity not in PEOPLE_ENTITIES:
            return redirect(url_for("admin_people"))
        from bari_lms.repositories.entidad import get_entity, update_entity
        if get_entity(entity, item_id) is None:
            flash("La persona solicitada no existe.", "danger")
            return redirect(url_for("admin_people"))
        data = entity_form_data(entity, request.form)
        error = validate_entity_payload(entity, data)
        if error:
            flash(error, "danger")
            return redirect(
                url_for("admin_people", edit_entity=entity, edit_id=item_id)
            )
        try:
            update_entity(entity, item_id, data)
            sync_linked_person_user(entity, item_id, data)
        except IntegrityError:
            get_db().rollback()
            flash(
                f"No fue posible actualizar {ENTITY_CONFIG[entity]['label'].lower()}. "
                "Verifica los datos ingresados.",
                "danger",
            )
            return redirect(
                url_for("admin_people", edit_entity=entity, edit_id=item_id)
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(
                url_for("admin_people", edit_entity=entity, edit_id=item_id)
            )
        flash(f"{ENTITY_CONFIG[entity]['label']} actualizada correctamente.", "success")
        return redirect(url_for("admin_people"))

    @app.post("/admin/people/<entity>/<item_id>/delete")
    @role_required("Administrador")
    def admin_people_delete(entity, item_id):
        if entity not in PEOPLE_ENTITIES:
            return redirect(url_for("admin_people"))
        from bari_lms.repositories.entidad import get_entity
        if get_entity(entity, item_id) is None:
            flash("La persona solicitada no existe.", "danger")
            return redirect(url_for("admin_people"))
        delete_linked_person_user(entity, item_id)
        flash(f"{ENTITY_CONFIG[entity]['label']} eliminada correctamente.", "success")
        return redirect(url_for("admin_people"))
