"""Repositorio de personas: contexto de gestión, vinculación persona-usuario."""

import uuid

from bari_lms.db import get_db, parse_uuid
from bari_lms.repositories._config import PEOPLE_ENTITIES, PERSON_USER_CONFIG
from bari_lms.repositories.entidad import get_entities, get_entity
from bari_lms.repositories.usuario import get_user_by_email
from bari_lms.services.security import hash_password


# ── Utilidades ───────────────────────────────────────────────────────────────

def person_full_name(data):
    return f"{data['nombres']} {data['apellidos']}".strip()


def generate_person_email(prefix, documento, email):
    clean_email = (email or "").strip().lower()
    if clean_email:
        return clean_email
    return f"{prefix}.{documento}@barilms.local"


# ── Contexto de vista ────────────────────────────────────────────────────────

def get_people_redirect_args(form_data, overrides=None):
    args = {
        "edit_entity": form_data.get("edit_entity"),
        "edit_id": parse_uuid(form_data.get("edit_id")),
    }
    args.update(overrides or {})
    return {key: value for key, value in args.items() if value not in (None, "")}


def normalize_people_context(args):
    edit_entity = args.get("edit_entity")
    edit_id = parse_uuid(args.get("edit_id"))
    if edit_entity not in PEOPLE_ENTITIES:
        edit_entity = None
        edit_id = None
    editing_item = get_entity(edit_entity, edit_id) if edit_entity and edit_id else None
    if edit_entity and editing_item is None:
        edit_entity = None
        edit_id = None
    regionales = get_entities("regional", order_by="nombre ASC")
    centros = get_entities("centro", order_by="nombre ASC")
    areas_academicas = get_entities("area", order_by="nombre ASC")
    return {
        "regionales": regionales,
        "coordinaciones": get_entities("coordinacion", order_by="nombre ASC"),
        "centros": centros,
        "areas_academicas": areas_academicas,
        "instructores": get_entities("instructor", order_by="nombres ASC, apellidos ASC"),
        "aprendices": get_entities("aprendiz", order_by="nombres ASC, apellidos ASC"),
        "administrativos": get_entities(
            "administrativo_persona", order_by="nombres ASC, apellidos ASC"
        ),
        "regional_map": {r["id"]: r["nombre"] for r in regionales},
        "centro_map": {c["id"]: c["nombre"] for c in centros},
        "area_map": {a["id"]: a["nombre"] for a in areas_academicas},
        "edit_entity": edit_entity,
        "edit_id": edit_id,
        "editing_item": editing_item,
    }


# ── Vinculación persona ↔ usuario ────────────────────────────────────────────

def create_linked_person_user(entity, item_id, data):
    config = PERSON_USER_CONFIG[entity]
    login_email = generate_person_email(
        config["email_prefix"], data["documento"], data.get("correo")
    )
    if get_user_by_email(login_email) is not None:
        raise ValueError(
            "Ya existe un usuario con el correo que se intenta asignar a la persona."
        )

    db = get_db()
    new_user_id = str(uuid.uuid7())
    db.execute(
        "INSERT INTO usuario (id, correo, contrasena_hash, nombre, activo) "
        "VALUES (?, ?, ?, ?, TRUE)",
        (
            new_user_id,
            login_email,
            hash_password(data["documento"]),
            person_full_name(data),
        ),
    )
    db.execute(
        """
        INSERT INTO usuario_perfil (id, usuario_id, perfil_id)
        SELECT ?, ?, p.id FROM perfil p WHERE p.nombre = ?
        ON CONFLICT (usuario_id, perfil_id) DO NOTHING
        """,
        (str(uuid.uuid7()), new_user_id, config["role"]),
    )
    db.execute(
        f"UPDATE {config['table']} SET {config['email_column']} = ?, {config['user_column']} = ? WHERE id = ?",
        (login_email, new_user_id, item_id),
    )
    db.commit()
    return new_user_id


def sync_linked_person_user(entity, item_id, data):
    item = get_entity(entity, item_id)
    if item is None:
        return

    config = PERSON_USER_CONFIG[entity]
    login_email = generate_person_email(
        config["email_prefix"], data["documento"], data.get("correo")
    )
    db = get_db()

    if item["user_id"]:
        existing_user = get_user_by_email(login_email)
        if existing_user is not None and existing_user["id"] != item["user_id"]:
            raise ValueError(
                "Ya existe un usuario con el correo que se intenta asignar a la persona."
            )
        db.execute(
            "UPDATE usuario SET correo = ?, contrasena_hash = ?, nombre = ?, activo = TRUE WHERE id = ?",
            (
                login_email,
                hash_password(data["documento"]),
                person_full_name(data),
                item["user_id"],
            ),
        )
        db.execute(
            """
            INSERT INTO usuario_perfil (id, usuario_id, perfil_id)
            SELECT ?, ?, p.id FROM perfil p WHERE p.nombre = ?
            ON CONFLICT (usuario_id, perfil_id) DO NOTHING
            """,
            (str(uuid.uuid7()), item["user_id"], config["role"]),
        )
        db.execute(
            f"UPDATE {config['table']} SET {config['email_column']} = ? WHERE id = ?",
            (login_email, item_id),
        )
        db.commit()
        return

    create_linked_person_user(entity, item_id, data)


def delete_linked_person_user(entity, item_id):
    item = get_entity(entity, item_id)
    if item is None or not item.get("user_id"):
        return
    db = get_db()
    db.execute("DELETE FROM usuario WHERE id = ?", (item["user_id"],))
    db.commit()
