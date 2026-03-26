"""
instructores.py — Seed for instructors, access profiles, and assigned fichas.

Depends on: estructura.py (must run first).

Creates 6 instructors with full chain:
    usuario → persona → instructor → usuario_perfil("Instructor") → ficha_formacion

Credentials (profile: Instructor) — password: Sena2024*
    juan.perez@sena.edu.co        (ficha 2900001)
    maria.lopez@sena.edu.co       (ficha 2900002)
    carlos.rodriguez@sena.edu.co  (ficha 2900003)
    adriana.suarez@sena.edu.co    (ficha 2900004)
    ricardo.mendoza@sena.edu.co   (ficha 2900005)
    elena.beltran@sena.edu.co     (ficha 2900006)

Run from project root:
    python database/seeds/extraSeeds/instructores.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "internal"))

from bari_lms.services.security import hash_password
from db import connect, resolve_id
from queries import SeedQueries
from data import generate_id, DATA_INSTRUCTORES, SEED_PASSWORD


def run(cur):
    print("  → Hashing password and resolving shared dependencies...")
    pw_hash = hash_password(SEED_PASSWORD)

    deps = {
        "centro":   resolve_id(cur, "centro", "nombre",
                               "Centro de Gestión de Mercados, Logística y TIC del Norte de Santander"),
        "coord":    resolve_id(cur, "coordinacion", "nombre",
                               "Coordinación de Tecnologías de la Información"),
        "area":     resolve_id(cur, "area", "nombre", "Análisis y Desarrollo de Software"),
        "proyecto": resolve_id(cur, "proyecto_formativo", "codigo", "PF-ADSO-001"),
        "programa": resolve_id(cur, "programa_formacion", "nombre", "Análisis y Desarrollo de Software"),
        "perfil":   resolve_id(cur, "perfil", "nombre", "Instructor"),
    }

    for correo, nombre_full, doc, tipo_doc_cod, nom, ape, sex_cod, num_ficha in DATA_INSTRUCTORES:
        print(f"  → Instructor: {correo}")

        tipo_doc_id = resolve_id(cur, "tipo_documento", "codigo", tipo_doc_cod)
        sexo_id     = resolve_id(cur, "sexo", "codigo", sex_cod)

        # 1. Usuario
        u_id   = generate_id()
        is_new = SeedQueries.INSERT_USUARIO.execute(cur, (u_id, correo, pw_hash, nombre_full))
        u_id   = resolve_id(cur, "usuario", "correo", correo)

        # 2. Persona (id = usuario id by schema design)
        SeedQueries.INSERT_PERSONA.execute(cur, (u_id, tipo_doc_id, doc, nom, ape, sexo_id))

        # 3. Instructor entity
        SeedQueries.INSERT_INSTRUCTOR.execute(cur, (generate_id(), u_id, deps["centro"], deps["area"]))
        inst_id = resolve_id(cur, "instructor", "persona_id", u_id)

        # 4. Profile link
        if deps["perfil"]:
            SeedQueries.INSERT_PERFIL_LINK.execute(cur, (generate_id(), u_id, deps["perfil"]))

        # 5. Ficha de formación
        SeedQueries.INSERT_FICHA.execute(cur, (
            generate_id(), num_ficha,
            deps["programa"], deps["coord"], deps["proyecto"], inst_id,
        ))

        print(f"    {'[NEW]' if is_new else '[EXISTING]'} Processed successfully.")


if __name__ == "__main__":
    print("[ Seed 02 - Instructores ] Starting...")
    print(f"  Password for all: {SEED_PASSWORD}")
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                run(cur)
            conn.commit()
        print("[ Seed 02 - Instructores ] Done.\n")
    except Exception as e:
        print(f"[ Seed 02 - Instructores ] Fatal Error: {e}")
        raise
