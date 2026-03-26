"""Repositorio de personas: contexto de gestión, vinculación persona-usuario."""

import uuid

from bari_lms.db import get_db, parse_uuid
from bari_lms.repositories._config import ENTITY_CONFIG, PEOPLE_ENTITIES, PERSON_USER_CONFIG
from bari_lms.repositories.entidad import get_entities, get_entity
from bari_lms.repositories.usuario import get_user_by_email
from bari_lms.services.security import hash_password


# ── Utilidades ───────────────────────────────────────────────────────────────

def person_full_name(data):
    return f"{data.get('nombres', '')} {data.get('apellidos', '')}".strip()


def generate_person_email(prefix, documento, correo_personal):
    clean = (correo_personal or "").strip().lower()
    if clean:
        return clean
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
        "instructores": get_entities("instructor", order_by="pe.nombres ASC, pe.apellidos ASC"),
        "aprendices": get_entities("aprendiz", order_by="pe.nombres ASC, pe.apellidos ASC"),
        "administrativos": get_entities(
            "administrativo_persona", order_by="pe.nombres ASC, pe.apellidos ASC"
        ),
        "regional_map": {r["id"]: r["nombre"] for r in regionales},
        "centro_map": {c["id"]: c["nombre"] for c in centros},
        "area_map": {a["id"]: a["nombre"] for a in areas_academicas},
        "edit_entity": edit_entity,
        "edit_id": edit_id,
        "editing_item": editing_item,
    }


# ── Vinculación persona ↔ usuario ────────────────────────────────────────────

def create_linked_person_user(entity, data):
    """Crea usuario, persona, usuario_perfil y la entidad de rol. Retorna el id del rol."""
    config = PERSON_USER_CONFIG[entity]
    entity_config = ENTITY_CONFIG[entity]

    nombres = (data.get("nombres") or "").strip().upper()
    apellidos = (data.get("apellidos") or "").strip().upper()
    numero_documento = (data.get("documento") or "").strip()
    correo_personal = (data.get("correo") or "").strip().lower() or None

    correo_institucional = generate_person_email(
        config["email_prefix"], numero_documento, correo_personal
    )
    if get_user_by_email(correo_institucional) is not None:
        raise ValueError(
            "Ya existe un usuario con el correo que se intenta asignar a la persona."
        )

    db = get_db()
    persona_id = str(uuid.uuid7())

    db.execute(
        "INSERT INTO usuario (id, correo_institucional, contrasena_hash, activo) "
        "VALUES (?, ?, ?, TRUE)",
        (persona_id, correo_institucional, hash_password(numero_documento)),
    )
    db.execute(
        "INSERT INTO persona (id, nombres, apellidos, numero_documento, correo_personal) "
        "VALUES (?, ?, ?, ?, ?)",
        (persona_id, nombres, apellidos, numero_documento, correo_personal),
    )
    db.execute(
        """
        INSERT INTO usuario_perfil (id, usuario_id, perfil_id)
        SELECT ?, ?, p.id FROM perfil p WHERE p.nombre = ?
        ON CONFLICT (usuario_id, perfil_id) DO NOTHING
        """,
        (str(uuid.uuid7()), persona_id, config["role"]),
    )

    role_id = str(uuid.uuid7())
    role_fields = ["persona_id"] + entity_config["fields"]
    columns = "id, " + ", ".join(role_fields)
    placeholders = ", ".join(["?"] * (len(role_fields) + 1))
    values = (role_id, persona_id) + tuple(data.get(f) for f in entity_config["fields"])
    db.execute(
        f"INSERT INTO {entity_config['table']} ({columns}) VALUES ({placeholders})",
        values,
    )
    db.commit()
    return role_id


def sync_linked_person_user(entity, item_id, data):
    """Actualiza los datos de persona y usuario vinculados a la entidad de rol."""
    item = get_entity(entity, item_id)
    if item is None:
        return

    config = PERSON_USER_CONFIG[entity]
    persona_id = item["persona_id"]

    nombres = (data.get("nombres") or "").strip().upper()
    apellidos = (data.get("apellidos") or "").strip().upper()
    numero_documento = (data.get("documento") or "").strip()
    correo_personal = (data.get("correo") or "").strip().lower() or None

    correo_institucional = generate_person_email(
        config["email_prefix"], numero_documento, correo_personal
    )
    existing = get_user_by_email(correo_institucional)
    if existing is not None and existing["id"] != persona_id:
        raise ValueError(
            "Ya existe un usuario con el correo que se intenta asignar a la persona."
        )

    db = get_db()
    db.execute(
        "UPDATE persona SET nombres = ?, apellidos = ?, numero_documento = ?, correo_personal = ? "
        "WHERE id = ?",
        (nombres, apellidos, numero_documento, correo_personal, persona_id),
    )
    db.execute(
        "UPDATE usuario SET correo_institucional = ? WHERE id = ?",
        (correo_institucional, persona_id),
    )
    db.commit()


def delete_linked_person_user(entity, item_id):
    """Elimina la entidad de rol, su persona y su usuario (en orden por restricciones FK)."""
    item = get_entity(entity, item_id)
    if item is None:
        return
    persona_id = item["persona_id"]
    config = PERSON_USER_CONFIG[entity]
    db = get_db()
    db.execute(f"DELETE FROM {config['table']} WHERE id = ?", (item_id,))
    db.execute("DELETE FROM persona WHERE id = ?", (persona_id,))
    db.execute("DELETE FROM usuario WHERE id = ?", (persona_id,))
    db.commit()
