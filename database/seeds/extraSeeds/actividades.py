"""
actividades.py — Seed for project activities, learning activities, and sections.

Depends on: estructura.py, instructores.py.

All actividades_proyecto are shared across fichas — they link to fase_proyecto,
which links to proyecto_formativo, which all fichas reference.

Chain:
    fase_proyecto
        └── actividad_proyecto  (creado_por → instructor)
                └── actividad_aprendizaje
                        └── seccion_actividad

Run from project root:
    python database/seeds/extraSeeds/actividades.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "internal"))

from db import connect, resolve_id
from queries import SeedQueries
from data import (
    generate_id,
    DATA_ACTIVIDADES_PROYECTO,
    DATA_ACTIVIDADES_APRENDIZAJE,
    DATA_SECCIONES,
)


def run(cur):
    # ── Actividades de Proyecto ────────────────────────────────────────────────
    print("  → actividad_proyecto...")
    for fase_nombre, act_nombre, instructor_correo in DATA_ACTIVIDADES_PROYECTO:
        fase_id      = resolve_id(cur, "fase_proyecto", "nombre", fase_nombre)
        instructor_id = resolve_id(cur, "usuario", "correo", instructor_correo)

        if fase_id is None:
            print(f"    [WARN] Fase not found: '{fase_nombre}' — skipping '{act_nombre}'")
            continue

        was_inserted = SeedQueries.INSERT_ACTIVIDAD_PROYECTO.execute(
            cur, (generate_id(), fase_id, act_nombre, instructor_id)
        )
        print(f"    {'[+]' if was_inserted else '[skipped]'} {act_nombre}")

    # ── Actividades de Aprendizaje ─────────────────────────────────────────────
    print("  → actividad_aprendizaje...")
    for act_proy_nombre, aa_nombre, descripcion, fecha_ini, fecha_fin, orden in DATA_ACTIVIDADES_APRENDIZAJE:
        act_proy_id = resolve_id(cur, "actividad_proyecto", "nombre", act_proy_nombre)

        if act_proy_id is None:
            print(f"    [WARN] Actividad proyecto not found: '{act_proy_nombre}' — skipping '{aa_nombre}'")
            continue

        was_inserted = SeedQueries.INSERT_ACTIVIDAD_APRENDIZAJE.execute(cur, (
            generate_id(), act_proy_id, aa_nombre,
            descripcion, fecha_ini, fecha_fin, orden,
            None,  # creado_por — not required for seed data
        ))
        print(f"    {'[+]' if was_inserted else '[skipped]'} {aa_nombre}")

    # ── Secciones de Actividad ─────────────────────────────────────────────────
    print("  → seccion_actividad...")
    for aa_nombre, sec_nombre, descripcion, orden in DATA_SECCIONES:
        aa_id = resolve_id(cur, "actividad_aprendizaje", "nombre", aa_nombre)

        if aa_id is None:
            print(f"    [WARN] Actividad aprendizaje not found: '{aa_nombre}' — skipping '{sec_nombre}'")
            continue

        was_inserted = SeedQueries.INSERT_SECCION_ACTIVIDAD.execute(cur, (
            generate_id(), aa_id, sec_nombre, descripcion, orden, None,
        ))
        print(f"    {'[+]' if was_inserted else '[skipped]'} {sec_nombre}")


if __name__ == "__main__":
    print("[ Seed 04 - Actividades ] Starting...")
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                run(cur)
            conn.commit()
        print("[ Seed 04 - Actividades ] Done.\n")
    except Exception as e:
        print(f"[ Seed 04 - Actividades ] Fatal Error: {e}")
        raise
