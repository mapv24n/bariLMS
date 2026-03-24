"""
Seed 01 — Estructura institucional y catálogos base.

Inserta (idempotente):
  • tipo_documento, sexo
  • regional, centro, coordinacion
  • red_conocimiento, area, nivel_formacion
  • proyecto_formativo + fases
  • programa_formacion

Ejecutar desde la raíz del proyecto:
    python database/seeds/01_estructura.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "internal"))

import psycopg  # noqa: E402

# ── IDs fijos — usados solo en el INSERT inicial.
# Si ya existe un registro con el mismo natural key, se descarta este UUID
# y se usa el real (resuelto con _resolve_id). No los uses como FK directamente.

TIPO_DOC_CC  = "10000000-0000-0000-0000-000000000001"
TIPO_DOC_TI  = "10000000-0000-0000-0000-000000000002"
TIPO_DOC_CE  = "10000000-0000-0000-0000-000000000003"

SEXO_M       = "20000000-0000-0000-0000-000000000001"
SEXO_F       = "20000000-0000-0000-0000-000000000002"

REGIONAL_1   = "30000000-0000-0000-0000-000000000001"
CENTRO_1     = "40000000-0000-0000-0000-000000000001"
COORD_1      = "50000000-0000-0000-0000-000000000001"

RED_TIC      = "60000000-0000-0000-0000-000000000001"
AREA_ADSO    = "70000000-0000-0000-0000-000000000001"

NIVEL_TEC    = "80000000-0000-0000-0000-000000000001"
NIVEL_AUX    = "80000000-0000-0000-0000-000000000002"

PROYECTO_1        = "90000000-0000-0000-0000-000000000001"
FASE_ANALISIS     = "90000000-0000-0000-0000-000000000002"
FASE_DISENO       = "90000000-0000-0000-0000-000000000003"
FASE_IMPLEMENTACION = "90000000-0000-0000-0000-000000000004"
FASE_PRUEBAS      = "90000000-0000-0000-0000-000000000005"

PROGRAMA_ADSO = "a0000000-0000-0000-0000-000000000001"


def connect():
    return psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE", "bari_lms"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", ""),
    )


def _resolve_id(cur, table, col, val):
    """Devuelve el UUID real de la fila encontrada por clave natural."""
    cur.execute(f"SELECT id FROM {table} WHERE {col} = %s", (val,))
    row = cur.fetchone()
    return str(row[0]) if row else None


def run(cur):
    # ── Catálogos ─────────────────────────────────────────────────────────────
    print("  → tipo_documento...")
    for fixed_id, codigo, nombre in [
        (TIPO_DOC_CC, "cc", "Cédula de Ciudadanía"),
        (TIPO_DOC_TI, "ti", "Tarjeta de Identidad"),
        (TIPO_DOC_CE, "ce", "Cédula de Extranjería"),
    ]:
        cur.execute(
            "INSERT INTO tipo_documento (id, codigo, nombre) VALUES (%s, %s, %s)"
            " ON CONFLICT DO NOTHING",
            (fixed_id, codigo, nombre),
        )
    tipo_doc_cc = _resolve_id(cur, "tipo_documento", "codigo", "cc")
    tipo_doc_ti = _resolve_id(cur, "tipo_documento", "codigo", "ti")
    tipo_doc_ce = _resolve_id(cur, "tipo_documento", "codigo", "ce")  # noqa: F841

    print("  → sexo...")
    for fixed_id, codigo, nombre in [
        (SEXO_M, "m", "Masculino"),
        (SEXO_F, "f", "Femenino"),
    ]:
        cur.execute(
            "INSERT INTO sexo (id, codigo, nombre) VALUES (%s, %s, %s)"
            " ON CONFLICT DO NOTHING",
            (fixed_id, codigo, nombre),
        )
    sexo_m = _resolve_id(cur, "sexo", "codigo", "m")  # noqa: F841
    sexo_f = _resolve_id(cur, "sexo", "codigo", "f")  # noqa: F841

    # ── Estructura institucional ──────────────────────────────────────────────
    print("  → regional...")
    cur.execute(
        "INSERT INTO regional (id, nombre) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        (REGIONAL_1, "Regional Norte de Santander"),
    )
    regional_id = _resolve_id(cur, "regional", "nombre", "Regional Norte de Santander")

    print("  → centro...")
    cur.execute(
        "INSERT INTO centro (id, regional_id, nombre) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
        (CENTRO_1, regional_id,
         "Centro de Gestión de Mercados, Logística y TIC del Norte de Santander"),
    )
    centro_id = _resolve_id(
        cur, "centro", "nombre",
        "Centro de Gestión de Mercados, Logística y TIC del Norte de Santander"
    )

    print("  → coordinacion...")
    cur.execute(
        "INSERT INTO coordinacion (id, centro_id, nombre) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
        (COORD_1, centro_id, "Coordinación de Tecnologías de la Información"),
    )
    coord_id = _resolve_id(cur, "coordinacion", "nombre", "Coordinación de Tecnologías de la Información")  # noqa: F841

    # ── Red de conocimiento / área ────────────────────────────────────────────
    print("  → red_conocimiento...")
    cur.execute(
        "INSERT INTO red_conocimiento (id, nombre) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        (RED_TIC, "Tecnología de la Información y las Comunicaciones"),
    )
    red_id = _resolve_id(cur, "red_conocimiento", "nombre", "Tecnología de la Información y las Comunicaciones")

    print("  → area...")
    cur.execute(
        "INSERT INTO area (id, red_conocimiento_id, nombre) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
        (AREA_ADSO, red_id, "Análisis y Desarrollo de Software"),
    )
    area_id = _resolve_id(cur, "area", "nombre", "Análisis y Desarrollo de Software")

    # ── Niveles de formación ──────────────────────────────────────────────────
    print("  → nivel_formacion...")
    for fixed_id, nombre in [(NIVEL_TEC, "Tecnólogo"), (NIVEL_AUX, "Auxiliar")]:
        cur.execute(
            "INSERT INTO nivel_formacion (id, nombre) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (fixed_id, nombre),
        )
    nivel_tec = _resolve_id(cur, "nivel_formacion", "nombre", "Tecnólogo")

    # ── Proyecto formativo + fases ────────────────────────────────────────────
    print("  → proyecto_formativo...")
    cur.execute(
        "INSERT INTO proyecto_formativo (id, codigo, nombre) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
        (PROYECTO_1, "PF-ADSO-001", "Sistema Integrado de Gestión de Aprendizaje (SIGA)"),
    )
    proyecto_id = _resolve_id(cur, "proyecto_formativo", "codigo", "PF-ADSO-001")

    print("  → fase_proyecto...")
    for fixed_id, nombre in [
        (FASE_ANALISIS,        "Análisis y Levantamiento de Requisitos"),
        (FASE_DISENO,          "Diseño de Solución"),
        (FASE_IMPLEMENTACION,  "Implementación"),
        (FASE_PRUEBAS,         "Pruebas y Despliegue"),
    ]:
        cur.execute(
            "INSERT INTO fase_proyecto (id, proyecto_formativo_id, nombre) VALUES (%s, %s, %s)"
            " ON CONFLICT DO NOTHING",
            (fixed_id, proyecto_id, nombre),
        )

    # ── Programa de formación ─────────────────────────────────────────────────
    print("  → programa_formacion...")
    cur.execute(
        "INSERT INTO programa_formacion (id, area_id, nivel_formacion_id, nombre)"
        " VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
        (PROGRAMA_ADSO, area_id, nivel_tec, "Análisis y Desarrollo de Software"),
    )


if __name__ == "__main__":
    print("[ Seed 01 ] Estructura institucional y catálogos")
    with connect() as conn:
        with conn.cursor() as cur:
            run(cur)
        conn.commit()
    print("[ Seed 01 ] Listo.\n")
