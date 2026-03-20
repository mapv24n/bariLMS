"""Repositorio académico: contexto y args de redirección para la gestión académica."""

from bari_lms.db import get_db, parse_uuid
from bari_lms.repositories._config import ACADEMIC_ENTITIES
from bari_lms.repositories.entidad import get_entities, get_entity


def academic_redirect_args(form_data, overrides=None):
    args = {
        "red_id": parse_uuid(form_data.get("red_id")),
        "area_id": parse_uuid(form_data.get("area_id")),
        "programa_id": parse_uuid(form_data.get("programa_id")),
        "nivel_id": parse_uuid(form_data.get("nivel_id")),
        "proyecto_formativo_id": parse_uuid(form_data.get("proyecto_formativo_id")),
        "fase_id": parse_uuid(form_data.get("fase_id")),
        "actividad_proyecto_id": parse_uuid(form_data.get("actividad_proyecto_id")),
    }
    args.update(overrides or {})
    return {key: value for key, value in args.items() if value}


def normalize_academic_context(args):  # noqa: C901
    red_id = parse_uuid(args.get("red_id"))
    area_id = parse_uuid(args.get("area_id"))
    programa_id = parse_uuid(args.get("programa_id"))
    nivel_id = parse_uuid(args.get("nivel_id"))
    proyecto_formativo_id = parse_uuid(args.get("proyecto_formativo_id"))
    fase_id = parse_uuid(args.get("fase_id"))
    actividad_proyecto_id = parse_uuid(args.get("actividad_proyecto_id"))
    edit_entity = args.get("edit_entity")
    edit_id = parse_uuid(args.get("edit_id"))

    red = get_entity("red", red_id)
    if red is None:
        red_id = area_id = programa_id = None

    area = get_entity("area", area_id)
    if area is None or (red_id and area["red_id"] != red_id):
        area = area_id = programa_id = None

    programa = get_entity("programa", programa_id)
    if programa is None or (area_id and programa["area_id"] != area_id):
        programa = programa_id = None

    nivel = get_entity("nivel", nivel_id)
    if nivel is None:
        nivel_id = None

    proyecto_formativo = get_entity("proyecto_formativo", proyecto_formativo_id)
    if proyecto_formativo is None:
        proyecto_formativo_id = fase_id = None

    fase_proyecto = get_entity("fase_proyecto", fase_id)
    if fase_proyecto is None or (
        proyecto_formativo_id
        and fase_proyecto["proyecto_formativo_id"] != proyecto_formativo_id
    ):
        fase_proyecto = fase_id = actividad_proyecto_id = None

    actividad_proyecto = get_entity("actividad_proyecto", actividad_proyecto_id)
    if actividad_proyecto is None or (
        fase_id and actividad_proyecto["fase_id"] != fase_id
    ):
        actividad_proyecto = actividad_proyecto_id = None

    if edit_entity not in ACADEMIC_ENTITIES:
        edit_entity = edit_id = None
    editing_item = get_entity(edit_entity, edit_id) if edit_entity and edit_id else None

    if edit_entity == "area" and (editing_item is None or editing_item["red_id"] != red_id):
        edit_entity = edit_id = None
    if edit_entity == "programa" and (editing_item is None or editing_item["area_id"] != area_id):
        edit_entity = edit_id = None
    if edit_entity == "ficha" and (editing_item is None or editing_item["programa_id"] != programa_id):
        edit_entity = edit_id = None
    if edit_entity == "fase_proyecto" and (
        editing_item is None or editing_item["proyecto_formativo_id"] != proyecto_formativo_id
    ):
        edit_entity = edit_id = None
    if edit_entity == "actividad_proyecto" and (
        editing_item is None or editing_item["fase_id"] != fase_id
    ):
        edit_entity = edit_id = None
    if edit_entity == "actividad_aprendizaje" and (
        editing_item is None or editing_item["actividad_proyecto_id"] != actividad_proyecto_id
    ):
        edit_entity = edit_id = None
    if edit_entity in {"red", "nivel", "proyecto_formativo"} and editing_item is None:
        edit_entity = edit_id = None

    # Fichas del programa seleccionado
    fichas = []
    if programa_id:
        fichas = get_db().execute(
            """
            SELECT f.id, f.numero, f.programa_formacion_id AS programa_id,
                   f.proyecto_formativo_id, f.coordinacion_id, f.instructor_id,
                   pf.nombre AS proyecto_formativo_nombre,
                   c.nombre  AS coordinacion_nombre,
                   i.nombres || ' ' || i.apellidos AS instructor_nombre
            FROM ficha_formacion f
            LEFT JOIN proyecto_formativo pf ON pf.id = f.proyecto_formativo_id
            JOIN coordinacion c ON c.id = f.coordinacion_id
            LEFT JOIN instructor i ON i.id = f.instructor_id
            WHERE f.programa_formacion_id = ?
            ORDER BY f.numero ASC
            """,
            (programa_id,),
        ).fetchall()

    # Instructores del área del programa
    instructores_area = []
    if programa:
        instructores_area = get_db().execute(
            """
            SELECT id, documento, nombres, apellidos, correo AS email, area_id, centro_id
            FROM instructor
            WHERE area_id = ?
            ORDER BY nombres ASC, apellidos ASC
            """,
            (programa["area_id"],),
        ).fetchall()

    return {
        "redes": get_entities("red", order_by="nombre ASC"),
        "areas": (
            get_entities("area", "red_conocimiento_id = ?", (red_id,), "nombre ASC")
            if red_id else []
        ),
        "niveles": (_niveles := get_entities("nivel", order_by="nombre ASC")),
        "nivel_map": {n["id"]: n["nombre"] for n in _niveles},
        "programas": (
            get_entities("programa", "area_id = ?", (area_id,), "nombre ASC")
            if area_id else []
        ),
        "fichas": fichas,
        "coordinaciones_disponibles": get_entities("coordinacion", order_by="nombre ASC"),
        "instructores_area": instructores_area,
        "proyectos_formativos": get_entities(
            "proyecto_formativo", order_by="codigo ASC, nombre ASC"
        ),
        "fases_proyecto": (
            get_entities(
                "fase_proyecto",
                "proyecto_formativo_id = ?",
                (proyecto_formativo_id,),
                "nombre ASC",
            )
            if proyecto_formativo_id else []
        ),
        "actividades_proyecto": (
            get_entities(
                "actividad_proyecto", "fase_proyecto_id = ?", (fase_id,), "nombre ASC"
            )
            if fase_id else []
        ),
        "actividades_aprendizaje": (
            get_entities(
                "actividad_aprendizaje",
                "actividad_proyecto_id = ?",
                (actividad_proyecto_id,),
                "nombre ASC",
            )
            if actividad_proyecto_id else []
        ),
        "selected_red": red,
        "selected_area": area,
        "selected_programa": programa,
        "selected_nivel": nivel,
        "selected_proyecto_formativo": proyecto_formativo,
        "selected_fase_proyecto": fase_proyecto,
        "selected_actividad_proyecto": actividad_proyecto,
        "edit_entity": edit_entity,
        "edit_id": edit_id,
        "editing_item": editing_item,
        "red_id": red_id,
        "area_id": area_id,
        "programa_id": programa_id,
        "nivel_id": nivel_id,
        "proyecto_formativo_id": proyecto_formativo_id,
        "fase_id": fase_id,
        "actividad_proyecto_id": actividad_proyecto_id,
    }
