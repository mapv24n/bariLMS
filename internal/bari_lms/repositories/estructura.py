"""Repositorio de estructura institucional: contexto y args de redirección."""

from bari_lms.db import parse_uuid
from bari_lms.repositories._config import ENTITY_CONFIG, STRUCTURE_ENTITIES
from bari_lms.repositories.entidad import get_entities, get_entity


def structure_redirect_args(form_data, overrides=None):
    args = {
        "regional_id": parse_uuid(form_data.get("regional_id")),
        "centro_id": parse_uuid(form_data.get("centro_id")),
        "coordinacion_id": parse_uuid(form_data.get("coordinacion_id")),
        "sede_id": parse_uuid(form_data.get("sede_id")),
    }
    args.update(overrides or {})
    return {key: value for key, value in args.items() if value}


def normalize_structure_context(args):
    regional_id = parse_uuid(args.get("regional_id"))
    centro_id = parse_uuid(args.get("centro_id"))
    coordinacion_id = parse_uuid(args.get("coordinacion_id"))
    sede_id = parse_uuid(args.get("sede_id"))
    edit_entity = args.get("edit_entity")
    edit_id = parse_uuid(args.get("edit_id"))

    regional = get_entity("regional", regional_id)
    if regional is None:
        regional_id = centro_id = coordinacion_id = sede_id = None

    centro = get_entity("centro", centro_id)
    if centro is None or (regional_id and centro["regional_id"] != regional_id):
        centro = centro_id = coordinacion_id = sede_id = None

    coordinacion = get_entity("coordinacion", coordinacion_id)
    if coordinacion is None or (centro_id and coordinacion["centro_id"] != centro_id):
        coordinacion = coordinacion_id = None

    sede = get_entity("sede", sede_id)
    if sede is None or (centro_id and sede["centro_id"] != centro_id):
        sede = sede_id = None

    if edit_entity not in ENTITY_CONFIG:
        edit_entity = edit_id = None

    editing_item = get_entity(edit_entity, edit_id) if edit_entity and edit_id else None

    if edit_entity == "regional" and editing_item is None:
        edit_entity = edit_id = None
    if edit_entity == "centro" and (editing_item is None or editing_item["regional_id"] != regional_id):
        edit_entity = edit_id = None
    if edit_entity in {"coordinacion", "sede"} and (editing_item is None or editing_item["centro_id"] != centro_id):
        edit_entity = edit_id = None
    if edit_entity not in STRUCTURE_ENTITIES and edit_entity is not None:
        edit_entity = edit_id = None
    if edit_entity == "ambiente" and (editing_item is None or editing_item["sede_id"] != sede_id):
        edit_entity = edit_id = None

    return {
        "selected_regional": regional,
        "selected_centro": centro,
        "selected_coordinacion": coordinacion,
        "selected_sede": sede,
        "areas_academicas": get_entities("area", order_by="nombre ASC"),
        "regionales": get_entities("regional", order_by="nombre ASC"),
        "centros": (
            get_entities("centro", "regional_id = ?", (regional_id,), "nombre ASC")
            if regional_id else []
        ),
        "coordinaciones": (
            get_entities("coordinacion", "centro_id = ?", (centro_id,), "nombre ASC")
            if centro_id else []
        ),
        "sedes": (
            get_entities("sede", "centro_id = ?", (centro_id,), "nombre ASC")
            if centro_id else []
        ),
        "ambientes": (
            get_entities("ambiente", "sede_id = ?", (sede_id,), "nombre ASC")
            if sede_id else []
        ),
        "edit_entity": edit_entity,
        "edit_id": edit_id,
        "editing_item": editing_item,
        "regional_id": regional_id,
        "centro_id": centro_id,
        "coordinacion_id": coordinacion_id,
        "sede_id": sede_id,
    }
