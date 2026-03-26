"""
Seed 02 — Instructores, perfil de acceso y fichas asignadas.

Depende de: 01_estructura.py (debe ejecutarse primero).

Crea 3 instructores con cadena completa:
    usuario → persona → instructor → usuario_perfil("Instructor")
Y 3 fichas de formación, una por instructor.

Credenciales (perfil: Instructor):
    juan.perez@sena.edu.co        / Sena2024*
    maria.lopez@sena.edu.co       / Sena2024*
    carlos.rodriguez@sena.edu.co  / Sena2024*

Ejecutar desde la raíz del proyecto:
    python database/seeds/02_instructores.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "internal"))

import psycopg  # noqa: E402
from bari_lms.services.security import hash_password  # noqa: E402

# ── IDs fijos de este seed ────────────────────────────────────────────────────
# usuario.id = persona.id (mismo UUID por diseño del esquema)
USR_INST1 = "b1000000-0000-0000-0000-000000000001"
USR_INST2 = "b1000000-0000-0000-0000-000000000002"
USR_INST3 = "b1000000-0000-0000-0000-000000000003"

INST1  = "b2000000-0000-0000-0000-000000000001"
INST2  = "b2000000-0000-0000-0000-000000000002"
INST3  = "b2000000-0000-0000-0000-000000000003"

FICHA1 = "b3000000-0000-0000-0000-000000000001"
FICHA2 = "b3000000-0000-0000-0000-000000000002"
FICHA3 = "b3000000-0000-0000-0000-000000000003"

PASSWORD = "Sena2024*"


def connect():
    return psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE", "bari_lms"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", ""),
    )


def _resolve_id(cur, table, col, val):
    cur.execute(f"SELECT id FROM {table} WHERE {col} = %s", (val,))
    row = cur.fetchone()
    return str(row[0]) if row else None


def run(cur):
    pw_hash = hash_password(PASSWORD)

    # ── Resolver IDs reales de seed 01 ───────────────────────────────────────
    tipo_doc_cc = _resolve_id(cur, "tipo_documento", "codigo", "cc")
    sexo_m      = _resolve_id(cur, "sexo", "codigo", "m")
    sexo_f      = _resolve_id(cur, "sexo", "codigo", "f")
    centro_id   = _resolve_id(cur, "centro", "nombre",
                               "Centro de Gestión de Mercados, Logística y TIC del Norte de Santander")
    coord_id    = _resolve_id(cur, "coordinacion", "nombre",
                               "Coordinación de Tecnologías de la Información")
    area_id     = _resolve_id(cur, "area", "nombre", "Análisis y Desarrollo de Software")
    proyecto_id = _resolve_id(cur, "proyecto_formativo", "codigo", "PF-ADSO-001")
    programa_id = _resolve_id(cur, "programa_formacion", "nombre", "Análisis y Desarrollo de Software")

    # ── Usuarios ──────────────────────────────────────────────────────────────
    print("  → usuario (instructores)...")
    instructores = [
        (USR_INST1, "juan.perez@sena.edu.co",         pw_hash, "Juan Carlos Pérez Martínez"),
        (USR_INST2, "maria.lopez@sena.edu.co",         pw_hash, "María Fernanda López Díaz"),
        (USR_INST3, "carlos.rodriguez@sena.edu.co",    pw_hash, "Carlos Alberto Rodríguez Gómez"),
    ]
    for row in instructores:
        cur.execute(
            "INSERT INTO usuario (id, correo, contrasena_hash, nombre, activo)"
            " VALUES (%s, %s, %s, %s, TRUE) ON CONFLICT DO NOTHING",
            row,
        )
    usr_inst1 = _resolve_id(cur, "usuario", "correo", "juan.perez@sena.edu.co")
    usr_inst2 = _resolve_id(cur, "usuario", "correo", "maria.lopez@sena.edu.co")
    usr_inst3 = _resolve_id(cur, "usuario", "correo", "carlos.rodriguez@sena.edu.co")

    # ── Personas (mismo UUID que usuario) ─────────────────────────────────────
    print("  → persona (instructores)...")
    for usr_id, doc, nombres, apellidos, sexo in [
        (usr_inst1, "10254871", "JUAN CARLOS",    "PÉREZ MARTÍNEZ",    sexo_m),
        (usr_inst2, "37584296", "MARÍA FERNANDA", "LÓPEZ DÍAZ",         sexo_f),
        (usr_inst3, "91345678", "CARLOS ALBERTO", "RODRÍGUEZ GÓMEZ",    sexo_m),
    ]:
        cur.execute(
            "INSERT INTO persona (id, tipo_documento_id, numero_documento, nombres, apellidos, sexo_id)"
            " VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            (usr_id, tipo_doc_cc, doc, nombres, apellidos, sexo),
        )

    # ── Instructores ──────────────────────────────────────────────────────────
    print("  → instructor...")
    for inst_id, usr_id in [(INST1, usr_inst1), (INST2, usr_inst2), (INST3, usr_inst3)]:
        cur.execute(
            "INSERT INTO instructor (id, persona_id, centro_id, area_id)"
            " VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
            (inst_id, usr_id, centro_id, area_id),
        )
    inst1 = _resolve_id(cur, "instructor", "persona_id", usr_inst1)
    inst2 = _resolve_id(cur, "instructor", "persona_id", usr_inst2)
    inst3 = _resolve_id(cur, "instructor", "persona_id", usr_inst3)

    # ── Perfil de acceso ──────────────────────────────────────────────────────
    print("  → usuario_perfil (Instructor)...")
    cur.execute(
        """
        INSERT INTO usuario_perfil (id, usuario_id, perfil_id)
        SELECT gen_random_uuid(), u, p.id
        FROM   (VALUES (%s::uuid), (%s::uuid), (%s::uuid)) AS t(u)
        JOIN   perfil p ON p.nombre = 'Instructor'
        ON CONFLICT (usuario_id, perfil_id) DO NOTHING
        """,
        (usr_inst1, usr_inst2, usr_inst3),
    )

    # ── Fichas de formación ───────────────────────────────────────────────────
    print("  → ficha_formacion...")
    for ficha_id, numero, inst_id in [
        (FICHA1, "2900001", inst1),
        (FICHA2, "2900002", inst2),
        (FICHA3, "2900003", inst3),
    ]:
        cur.execute(
            """
            INSERT INTO ficha_formacion
                (id, numero, programa_formacion_id, coordinacion_id, proyecto_formativo_id, instructor_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (ficha_id, numero, programa_id, coord_id, proyecto_id, inst_id),
        )


if __name__ == "__main__":
    print("[ Seed 02 ] Instructores y fichas")
    print(f"            Contraseña de todos: {PASSWORD}")
    with connect() as conn:
        with conn.cursor() as cur:
            run(cur)
        conn.commit()
    print("[ Seed 02 ] Listo.\n")

# Sena2024*