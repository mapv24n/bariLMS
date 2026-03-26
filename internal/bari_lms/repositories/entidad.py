"""Repositorio genérico de entidades: CRUD, validación y utilidades de formulario."""

import uuid

from bari_lms.db import get_db, parse_int
from bari_lms.repositories._config import ENTITY_CONFIG


# ── Consultas ────────────────────────────────────────────────────────────────

def entity_select_clause(entity):
    config = ENTITY_CONFIG[entity]
    alias_map = config.get("select_aliases", {})
    table = config["table"]
    fields = [f"{table}.id"]
    for field in config["fields"]:
        alias = alias_map.get(field)
        col = f"{table}.{field}"
        fields.append(f"{col} AS {alias}" if alias else col)
    extra = config.get("extra_select")
    if extra:
        fields.append(extra)
    return ", ".join(fields)


def get_entity(entity, item_id):
    if entity not in ENTITY_CONFIG or item_id is None:
        return None
    config = ENTITY_CONFIG[entity]
    table = config["table"]
    join = config.get("join", "")
    return get_db().execute(
        f"SELECT {entity_select_clause(entity)} FROM {table} {join} WHERE {table}.id = ?",
        (item_id,),
    ).fetchone()


def get_entities(entity, where=None, params=(), order_by="id DESC"):
    config = ENTITY_CONFIG[entity]
    table = config["table"]
    join = config.get("join", "")
    sql = f"SELECT {entity_select_clause(entity)} FROM {table} {join}"
    if where:
        sql += f" WHERE {where}"
    sql += f" ORDER BY {order_by}"
    return get_db().execute(sql, params).fetchall()


# ── Mutaciones ───────────────────────────────────────────────────────────────

def insert_entity(entity, data):
    config = ENTITY_CONFIG[entity]
    entity_id = str(uuid.uuid7())
    columns = "id, " + ", ".join(config["fields"])
    placeholders = ", ".join(["?"] * (len(config["fields"]) + 1))
    values = (entity_id,) + tuple(data[field] for field in config["fields"])
    cursor = get_db().execute(
        f"INSERT INTO {config['table']} ({columns}) VALUES ({placeholders}) RETURNING id",
        values,
    )
    get_db().commit()
    return cursor.fetchone()["id"]


def update_entity(entity, item_id, data):
    config = ENTITY_CONFIG[entity]
    assignments = ", ".join([f"{field} = ?" for field in config["fields"]])
    values = tuple(data[field] for field in config["fields"]) + (item_id,)
    get_db().execute(f"UPDATE {config['table']} SET {assignments} WHERE id = ?", values)
    get_db().commit()


def delete_entity(entity, item_id):
    get_db().execute(
        f"DELETE FROM {ENTITY_CONFIG[entity]['table']} WHERE id = ?", (item_id,)
    )
    get_db().commit()


# ── Formularios ──────────────────────────────────────────────────────────────

def entity_form_data(entity, form):
    data = {}
    config = ENTITY_CONFIG[entity]
    form_to_db = config.get("form_to_db", {})
    all_fields = config["fields"] + config.get("persona_form_fields", [])
    for field in all_fields:
        form_field = next(
            (name for name, db_name in form_to_db.items() if db_name == field), field
        )
        values = [value.strip() for value in form.getlist(form_field)]
        raw = next((value for value in reversed(values) if value != ""), "")
        if field.endswith("_id"):
            data[field] = raw or None
        elif field == "capacidad":
            data[field] = parse_int(raw) if raw else None
        else:
            data[field] = raw
    return data


# ── Validación ───────────────────────────────────────────────────────────────

def validate_entity_payload(entity, data):
    config = ENTITY_CONFIG[entity]
    for field in config["required"]:
        if data.get(field) in (None, ""):
            return f"El campo {field.replace('_', ' ')} es obligatorio."
    if entity == "ambiente" and data["capacidad"] is not None and data["capacidad"] < 0:
        return "La capacidad no puede ser negativa."
    if entity == "instructor" and get_entity("centro", data["centro_id"]) is None:
        return "El centro de formación seleccionado no existe."
    if (
        entity == "instructor"
        and data.get("area_id") is not None
        and get_entity("area", data["area_id"]) is None
    ):
        return "El área académica seleccionada no existe."
    if entity == "aprendiz" and get_entity("regional", data["regional_id"]) is None:
        return "La regional seleccionada no existe."
    if entity == "ficha" and data["instructor_id"] in ("", None):
        data["instructor_id"] = None
    return None


def validate_academic_payload(entity, data):
    error = validate_entity_payload(entity, data)
    if error:
        return error
    if entity == "programa":
        if data.get("area_id") is None or data.get("nivel_formacion_id") is None:
            return "El programa debe tener área y nivel de formación."
        if get_entity("area", data["area_id"]) is None:
            return "El área seleccionada no existe."
        if get_entity("nivel", data["nivel_formacion_id"]) is None:
            return "El nivel de formación seleccionado no existe."
    if entity == "ficha":
        programa = get_entity("programa", data["programa_formacion_id"])
        if programa is None:
            return "El programa seleccionado no existe."
        if get_entity("proyecto_formativo", data["proyecto_formativo_id"]) is None:
            return "El proyecto formativo seleccionado no existe."
        coordinacion = get_entity("coordinacion", data["coordinacion_id"])
        if coordinacion is None:
            return "La coordinación seleccionada no existe."
        if data.get("instructor_id"):
            instructor = get_entity("instructor", data["instructor_id"])
            if instructor is None:
                return "El instructor seleccionado no existe."
            if not instructor.get("area_id") or instructor["area_id"] != programa["area_id"]:
                return "El instructor asignado debe pertenecer a la misma área del programa."
            centro_coordinacion = get_entity("centro", coordinacion["centro_id"])
            if centro_coordinacion is None or instructor["centro_id"] != centro_coordinacion["id"]:
                return "El instructor asignado debe pertenecer al centro de formación de la coordinación."
    if entity == "fase_proyecto" and get_entity("proyecto_formativo", data["proyecto_formativo_id"]) is None:
        return "El proyecto formativo seleccionado no existe."
    if entity == "actividad_proyecto" and get_entity("fase_proyecto", data["fase_proyecto_id"]) is None:
        return "La fase seleccionada no existe."
    if entity == "actividad_aprendizaje" and get_entity("actividad_proyecto", data["actividad_proyecto_id"]) is None:
        return "La actividad de proyecto seleccionada no existe."
    return None
