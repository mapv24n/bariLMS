"""
aprendices.py — Seed for apprentices, enrollments, and EP companies.

Depends on: estructura.py, instructores.py.

Creates 12 apprentices (2 per ficha, 6 fichas) with varied states,
4 companies, and ficha_aprendiz enrollment records.

The company ↔ apprentice link (contrato_aprendizaje) lives in a separate
EP seed — this file only handles the formation-stage data.

Credentials (profile: Aprendiz) — password: Sena2024*
    Ficha 2900001: ana.gomez, luis.torres
    Ficha 2900002: sofia.mendez, andres.ruiz
    Ficha 2900003: camila.vargas, miguel.castro
    Ficha 2900004: mario.duarte, claudia.nieto
    Ficha 2900005: felipe.basto, paola.ortiz
    Ficha 2900006: jorge.vivas, diana.solano
    (all @aprendiz.sena.edu.co)

Run from project root:
    python database/seeds/extraSeeds/aprendices.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "internal"))

from bari_lms.services.security import hash_password
from db import connect, resolve_id
from queries import SeedQueries
from data import generate_id, DATA_APRENDICES, DATA_EMPRESAS, SEED_PASSWORD


def run(cur):
    print("  → Resolving dependencies...")
    pw_hash = hash_password(SEED_PASSWORD)

    regional_id = resolve_id(cur, "regional", "nombre", "Regional Norte de Santander")
    perfil_id   = resolve_id(cur, "perfil", "nombre", "Aprendiz")

    # ── Companies ──────────────────────────────────────────────────────────────
    print("  → empresa...")
    for razon, nit, sector, correo, tel in DATA_EMPRESAS:
        was_inserted = SeedQueries.INSERT_EMPRESA.execute(cur, (generate_id(), razon, nit, sector, correo, tel))
        print(f"    {'[+]' if was_inserted else '[skipped]'} {razon}")

    # ── Apprentices & Enrollments ──────────────────────────────────────────────
    print("  → aprendices...")
    for correo, full_n, doc, tipo_doc_cod, nom, ape, sex_cod, f_num, estado in DATA_APRENDICES:
        print(f"    - {correo}")

        tipo_doc_id = resolve_id(cur, "tipo_documento", "codigo", tipo_doc_cod)
        sexo_id     = resolve_id(cur, "sexo", "codigo", sex_cod)

        # A. Usuario
        u_id   = generate_id()
        is_new = SeedQueries.INSERT_USUARIO.execute(cur, (u_id, correo, pw_hash, full_n))
        u_id   = resolve_id(cur, "usuario", "correo", correo)

        # B. Persona
        SeedQueries.INSERT_PERSONA.execute(cur, (u_id, tipo_doc_id, doc, nom, ape, sexo_id))

        # C. Aprendiz entity
        SeedQueries.INSERT_APRENDIZ.execute(cur, (generate_id(), u_id, regional_id))
        apr_id = resolve_id(cur, "aprendiz", "persona_id", u_id)

        # D. Profile link
        if perfil_id:
            SeedQueries.INSERT_PERFIL_LINK.execute(cur, (generate_id(), u_id, perfil_id))

        # E. Ficha enrollment
        ficha_id = resolve_id(cur, "ficha_formacion", "numero", f_num)
        if ficha_id:
            SeedQueries.INSERT_FICHA_APRENDIZ.execute(cur, (
                generate_id(), ficha_id, apr_id, estado,
            ))

        print(f"      {'[NEW]' if is_new else '[EXISTING]'}")


if __name__ == "__main__":
    print("[ Seed 03 - Aprendices ] Starting...")
    print(f"  Password for all: {SEED_PASSWORD}")
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                run(cur)
            conn.commit()
        print("[ Seed 03 - Aprendices ] Done.\n")
    except Exception as e:
        print(f"[ Seed 03 - Aprendices ] Fatal Error: {e}")
        raise
