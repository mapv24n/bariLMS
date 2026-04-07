"""
estructura.py — Seed for institutional structure and base catalogs.

Inserts (idempotent):
  tipo_documento, sexo, nivel_formacion
  regional, centro, coordinacion
  red_conocimiento, area, programa_formacion
  proyecto_formativo, fase_proyecto

Run from project root:
    python database/seeds/extraSeeds/estructura.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "internal"))

from db import connect, resolve_id
from queries import SeedQueries
from data import (
    generate_id,
    DATA_TIPO_DOCUMENTO,
    DATA_SEXO,
    DATA_NIVELES_FORMACION,
    DATA_REGIONALES,
    DATA_CENTROS,
    DATA_COORDINACIONES,
    DATA_REDES,
    DATA_AREAS,
    DATA_PROGRAMAS,
    DATA_PROYECTOS,
    DATA_FASES,
)


def run(cur):
    print("  → tipo_documento...")
    for codigo, nombre in DATA_TIPO_DOCUMENTO:
        was_inserted = SeedQueries.INSERT_TIPO_DOC.execute(cur, (generate_id(), codigo, nombre))
        print(f"    {'[+]' if was_inserted else '[skipped]'} {codigo}")

    print("  → sexo...")
    for codigo, nombre in DATA_SEXO:
        SeedQueries.INSERT_SEXO.execute(cur, (generate_id(), codigo, nombre))

    print("  → nivel_formacion...")
    for (nombre,) in DATA_NIVELES_FORMACION:
        SeedQueries.INSERT_NIVEL_FORMACION.execute(cur, (generate_id(), nombre))

    print("  → regional...")
    for (nombre,) in DATA_REGIONALES:
        SeedQueries.INSERT_REGIONAL.execute(cur, (generate_id(), nombre))

    print("  → centro...")
    for regional_nombre, centro_nombre in DATA_CENTROS:
        regional_id = resolve_id(cur, "regional", "nombre", regional_nombre)
        SeedQueries.INSERT_CENTRO.execute(cur, (generate_id(), regional_id, centro_nombre))

    print("  → coordinacion...")
    for centro_nombre, coord_nombre in DATA_COORDINACIONES:
        centro_id = resolve_id(cur, "centro", "nombre", centro_nombre)
        SeedQueries.INSERT_COORDINACION.execute(cur, (generate_id(), centro_id, coord_nombre))

    print("  → red_conocimiento...")
    for (nombre,) in DATA_REDES:
        SeedQueries.INSERT_RED.execute(cur, (generate_id(), nombre))

    print("  → area...")
    for red_nombre, area_nombre in DATA_AREAS:
        red_id = resolve_id(cur, "red_conocimiento", "nombre", red_nombre)
        SeedQueries.INSERT_AREA.execute(cur, (generate_id(), red_id, area_nombre))

    print("  → nivel_formacion + programa_formacion...")
    for area_nombre, nivel_nombre, programa_nombre in DATA_PROGRAMAS:
        area_id  = resolve_id(cur, "area", "nombre", area_nombre)
        nivel_id = resolve_id(cur, "nivel_formacion", "nombre", nivel_nombre)
        SeedQueries.INSERT_PROGRAMA.execute(cur, (generate_id(), area_id, nivel_id, programa_nombre))

    print("  → proyecto_formativo...")
    for codigo, nombre in DATA_PROYECTOS:
        SeedQueries.INSERT_PROYECTO.execute(cur, (generate_id(), codigo, nombre))

    print("  → fase_proyecto...")
    for proyecto_codigo, fase_nombre in DATA_FASES:
        proyecto_id = resolve_id(cur, "proyecto_formativo", "codigo", proyecto_codigo)
        SeedQueries.INSERT_FASE.execute(cur, (generate_id(), proyecto_id, fase_nombre))


if __name__ == "__main__":
    print("[ Seed 01 - Estructura ] Starting...")
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                run(cur)
            conn.commit()
        print("[ Seed 01 - Estructura ] Done.\n")
    except Exception as e:
        print(f"[ Seed 01 - Estructura ] Fatal Error: {e}")
        raise
