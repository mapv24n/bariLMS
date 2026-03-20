#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
Seed PostgreSQL: Fichas 3115418 (ADSI) y 3115419 (Administración Financiera)
de la instructora Diana Beltrán.

Crea:
  - 15 aprendices por ficha (5 compartidos + 10 exclusivos c/u)
  - 4 fases por proyecto formativo
  - 1 actividad de proyecto por fase
  - 1 guía de ejemplo por actividad de proyecto (en guia_actividad_proyecto)
  - Las actividades de aprendizaje las crea el instructor desde la app

Ejecutar: python seed_pg.py
Idempotente: se puede correr varias veces sin duplicar datos.
"""
import os

import psycopg
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

# ── Conexión ─────────────────────────────────────────────────────────────────
conn = psycopg.connect(
    host=os.environ.get("PGHOST", "127.0.0.1"),
    port=int(os.environ.get("PGPORT", "5432")),
    dbname=os.environ.get("PGDATABASE", "bari_lms_postgresql.sql"),
    user=os.environ.get("PGUSER", "postgres"),
    password=os.environ.get("PGPASSWORD", ""),
)
conn.autocommit = False


def q(sql, params=()):
    cur = conn.cursor()
    cur.execute(sql.replace("?", "%s"), params)
    return cur


def first(sql, params=()):
    cur = q(sql, params)
    row = cur.fetchone()
    cur.close()
    return row[0] if row else None


def commit():
    conn.commit()


# ── Aprendices ────────────────────────────────────────────────────────────────
COMPARTIDOS = [
    ("1001001001", "Carlos",      "Mendoza García"),
    ("1001001002", "Laura",       "Jiménez Pérez"),
    ("1001001003", "Andrés",      "Morales Torres"),
    ("1001001004", "Valentina",   "Ríos Castillo"),
    ("1001001005", "Miguel",      "Torres Ruiz"),
]

SOLO_ADSI = [
    ("1001001006", "Sebastián",   "Gómez López"),
    ("1001001007", "Isabella",    "Vargas Montoya"),
    ("1001001008", "Daniel",      "Herrera Sánchez"),
    ("1001001009", "Camila",      "Ospina Restrepo"),
    ("1001001010", "Santiago",    "Reyes Méndez"),
    ("1001001011", "Alejandro",   "Castro Silva"),
    ("1001001012", "Mariana",     "López Bermúdez"),
    ("1001001013", "David",       "Ríos Palomino"),
    ("1001001014", "Sara",        "González Muñoz"),
    ("1001001015", "Juan Pablo",  "Cardona Vélez"),
]

SOLO_ADMIN = [
    ("1001001016", "Gabriela",    "Suárez Vega"),
    ("1001001017", "Felipe",      "Castro Díaz"),
    ("1001001018", "Natalia",     "Ramos Ortega"),
    ("1001001019", "Julián",      "Peña Vargas"),
    ("1001001020", "María José",  "Rojas Fuentes"),
    ("1001001021", "Sofía",       "Martínez Aguilar"),
    ("1001001022", "Nicolás",     "Arango Patiño"),
    ("1001001023", "Valeria",     "Cárdenas Ospina"),
    ("1001001024", "Juan Sebastián", "Mora Guzmán"),
    ("1001001025", "Paula Andrea","Rueda Torres"),
]

# ── Estructura de fases y actividades de proyecto ────────────────────────────
# (El instructor creará las actividades de aprendizaje desde la app)
# Guía de ejemplo: enlace a un documento de Google Drive público de SENA

GUIA_EJEMPLO_ADSI   = "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUU41JPKl/view"
GUIA_EJEMPLO_ADMIN  = "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUU41JPKl/view"

FASES_ADSI = [
    {
        "nombre": "Fase 1: Direccionamiento",
        "actividad_proyecto": "Análisis de Requisitos del Sistema",
        "guia_nombre": "Guía 1 — Levantamiento y análisis de requisitos",
        "guia_url": GUIA_EJEMPLO_ADSI,
    },
    {
        "nombre": "Fase 2: Planeación",
        "actividad_proyecto": "Diseño de la Arquitectura del Software",
        "guia_nombre": "Guía 2 — Diseño arquitectónico y modelado de datos",
        "guia_url": GUIA_EJEMPLO_ADSI,
    },
    {
        "nombre": "Fase 3: Ejecución",
        "actividad_proyecto": "Desarrollo e Implementación del Software",
        "guia_nombre": "Guía 3 — Desarrollo, pruebas e integración",
        "guia_url": GUIA_EJEMPLO_ADSI,
    },
    {
        "nombre": "Fase 4: Socialización",
        "actividad_proyecto": "Entrega y Presentación del Producto",
        "guia_nombre": "Guía 4 — Presentación, documentación y cierre",
        "guia_url": GUIA_EJEMPLO_ADSI,
    },
]

FASES_ADMIN = [
    {
        "nombre": "Fase 1: Direccionamiento",
        "actividad_proyecto": "Diagnóstico Financiero Empresarial",
        "guia_nombre": "Guía 1 — Diagnóstico y análisis del entorno financiero",
        "guia_url": GUIA_EJEMPLO_ADMIN,
    },
    {
        "nombre": "Fase 2: Planeación",
        "actividad_proyecto": "Plan Financiero y Presupuesto",
        "guia_nombre": "Guía 2 — Elaboración del plan financiero y presupuestal",
        "guia_url": GUIA_EJEMPLO_ADMIN,
    },
    {
        "nombre": "Fase 3: Ejecución",
        "actividad_proyecto": "Implementación Contable y Tributaria",
        "guia_nombre": "Guía 3 — Registro contable, impuestos y reportes",
        "guia_url": GUIA_EJEMPLO_ADMIN,
    },
    {
        "nombre": "Fase 4: Socialización",
        "actividad_proyecto": "Presentación de Resultados Financieros",
        "guia_nombre": "Guía 4 — Informe final y socialización de resultados",
        "guia_url": GUIA_EJEMPLO_ADMIN,
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
def run():
    print("═" * 65)
    print("  SEED PostgreSQL — Fichas Diana Beltrán")
    print("═" * 65)

    # ── 1. Infraestructura base ───────────────────────────────────────────────
    regional_id = first("SELECT id FROM regional LIMIT 1")
    if not regional_id:
        regional_id = first(
            "INSERT INTO regional (nombre) VALUES (%s) RETURNING id",
            ("Regional Distrito Capital",)
        )
        commit()
        print(f"✓ Regional creada id={regional_id}")
    else:
        print(f"✓ Regional existente id={regional_id}")

    centro_id = first("SELECT id FROM centro LIMIT 1")
    if not centro_id:
        centro_id = first(
            "INSERT INTO centro (id_regional, nombre) VALUES (%s, %s) RETURNING id",
            (regional_id, "Centro de Gestión de Mercados, Logística y TI")
        )
        commit()
        print(f"✓ Centro creado id={centro_id}")
    else:
        print(f"✓ Centro existente id={centro_id}")

    coord_id = first("SELECT id FROM coordinacion LIMIT 1")
    if not coord_id:
        coord_id = first(
            "INSERT INTO coordinacion (id_centro, nombre) VALUES (%s, %s) RETURNING id",
            (centro_id, "Coordinación Académica")
        )
        commit()
        print(f"✓ Coordinación creada id={coord_id}")
    else:
        print(f"✓ Coordinación existente id={coord_id}")

    # ── 2. Redes y áreas ─────────────────────────────────────────────────────
    red_ti_id = first(
        "SELECT id FROM red_conocimiento WHERE nombre = %s",
        ("Tecnología de la Información",)
    )
    if not red_ti_id:
        red_ti_id = first(
            "INSERT INTO red_conocimiento (nombre) VALUES (%s) RETURNING id",
            ("Tecnología de la Información",)
        )
        commit()
    print(f"✓ Red TI id={red_ti_id}")

    red_fin_id = first(
        "SELECT id FROM red_conocimiento WHERE nombre = %s",
        ("Financiero y Contable",)
    )
    if not red_fin_id:
        red_fin_id = first(
            "INSERT INTO red_conocimiento (nombre) VALUES (%s) RETURNING id",
            ("Financiero y Contable",)
        )
        commit()
    print(f"✓ Red Financiero id={red_fin_id}")

    area_soft_id = first(
        "SELECT id FROM area WHERE nombre = %s AND id_red_conocimiento = %s",
        ("Desarrollo de Software", red_ti_id)
    )
    if not area_soft_id:
        area_soft_id = first(
            "INSERT INTO area (id_red_conocimiento, nombre) VALUES (%s, %s) RETURNING id",
            (red_ti_id, "Desarrollo de Software")
        )
        commit()
    print(f"✓ Área Software id={area_soft_id}")

    area_admin_id = first(
        "SELECT id FROM area WHERE nombre = %s AND id_red_conocimiento = %s",
        ("Administración Financiera", red_fin_id)
    )
    if not area_admin_id:
        area_admin_id = first(
            "INSERT INTO area (id_red_conocimiento, nombre) VALUES (%s, %s) RETURNING id",
            (red_fin_id, "Administración Financiera")
        )
        commit()
    print(f"✓ Área Admin Financiera id={area_admin_id}")

    # ── 3. Niveles ────────────────────────────────────────────────────────────
    nivel_tec_id = first("SELECT id FROM nivel_formacion WHERE nombre = %s", ("Tecnólogo",))
    if not nivel_tec_id:
        nivel_tec_id = first("SELECT id FROM nivel_formacion LIMIT 1")
    print(f"✓ Nivel Tecnólogo id={nivel_tec_id}")

    # ── 4. Programas de formación ─────────────────────────────────────────────
    prog_adsi_id = first(
        "SELECT id FROM programa_formacion WHERE nombre = %s",
        ("Análisis y Desarrollo de Software",)
    )
    if not prog_adsi_id:
        prog_adsi_id = first(
            "INSERT INTO programa_formacion (id_area, id_nivel_formacion, nombre) VALUES (%s,%s,%s) RETURNING id",
            (area_soft_id, nivel_tec_id, "Análisis y Desarrollo de Software")
        )
        commit()
    print(f"✓ Programa ADSI id={prog_adsi_id}")

    prog_admin_id = first(
        "SELECT id FROM programa_formacion WHERE nombre = %s",
        ("Administración Financiera",)
    )
    if not prog_admin_id:
        prog_admin_id = first(
            "INSERT INTO programa_formacion (id_area, id_nivel_formacion, nombre) VALUES (%s,%s,%s) RETURNING id",
            (area_admin_id, nivel_tec_id, "Administración Financiera")
        )
        commit()
    print(f"✓ Programa Admin Financiera id={prog_admin_id}")

    # ── 5. Proyectos formativos ───────────────────────────────────────────────
    pf_adsi_id = first(
        "SELECT id FROM proyecto_formativo WHERE codigo = %s", ("PF-ADSI-2025",)
    )
    if not pf_adsi_id:
        pf_adsi_id = first(
            "INSERT INTO proyecto_formativo (codigo, nombre) VALUES (%s,%s) RETURNING id",
            ("PF-ADSI-2025", "Desarrollo de Soluciones de Software a la Medida")
        )
        commit()
    print(f"✓ Proyecto Formativo ADSI id={pf_adsi_id}")

    pf_admin_id = first(
        "SELECT id FROM proyecto_formativo WHERE codigo = %s", ("PF-ADMIN-2025",)
    )
    if not pf_admin_id:
        pf_admin_id = first(
            "INSERT INTO proyecto_formativo (codigo, nombre) VALUES (%s,%s) RETURNING id",
            ("PF-ADMIN-2025", "Gestión Contable y Financiera Empresarial")
        )
        commit()
    print(f"✓ Proyecto Formativo Admin Financiera id={pf_admin_id}")

    # ── 6. Instructora Diana Beltrán ──────────────────────────────────────────
    diana_user_id = first(
        "SELECT id FROM usuario WHERE lower(correo) = %s",
        ("instructor@senalearn.edu.co",)
    )
    if not diana_user_id:
        print("⚠ No se encontró usuario instructor@senalearn.edu.co")
        diana_instructor_id = None
    else:
        diana_instructor_id = first(
            "SELECT id FROM instructor WHERE id_usuario = %s", (diana_user_id,)
        )
        if not diana_instructor_id:
            diana_instructor_id = first(
                """INSERT INTO instructor
                   (id_centro, id_area, documento, nombres, apellidos, correo, id_usuario, genero)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                (centro_id, area_soft_id, "52987654", "Diana", "Beltrán",
                 "instructor@senalearn.edu.co", diana_user_id, "F")
            )
            commit()
            print(f"✓ Instructora Diana Beltrán creada id={diana_instructor_id}")
        else:
            q("UPDATE instructor SET id_area=%s, genero='F' WHERE id=%s",
              (area_soft_id, diana_instructor_id))
            commit()
            print(f"✓ Instructora Diana Beltrán id={diana_instructor_id} (actualizada)")

    # ── 7. Fichas de formación ────────────────────────────────────────────────
    ficha_adsi_id = first(
        "SELECT id FROM ficha_formacion WHERE numero = %s", ("3115418",)
    )
    if not ficha_adsi_id:
        ficha_adsi_id = first(
            """INSERT INTO ficha_formacion
               (numero, id_programa_formacion, id_proyecto_formativo, id_coordinacion, id_instructor)
               VALUES (%s,%s,%s,%s,%s) RETURNING id""",
            ("3115418", prog_adsi_id, pf_adsi_id, coord_id, diana_instructor_id)
        )
        commit()
        print(f"✓ Ficha 3115418 (ADSI) creada id={ficha_adsi_id}")
    else:
        q("""UPDATE ficha_formacion
             SET id_instructor=%s, id_proyecto_formativo=%s
             WHERE id=%s""",
          (diana_instructor_id, pf_adsi_id, ficha_adsi_id))
        commit()
        print(f"✓ Ficha 3115418 (ADSI) existente id={ficha_adsi_id} (actualizada)")

    ficha_admin_id = first(
        "SELECT id FROM ficha_formacion WHERE numero = %s", ("3115419",)
    )
    if not ficha_admin_id:
        ficha_admin_id = first(
            """INSERT INTO ficha_formacion
               (numero, id_programa_formacion, id_proyecto_formativo, id_coordinacion, id_instructor)
               VALUES (%s,%s,%s,%s,%s) RETURNING id""",
            ("3115419", prog_admin_id, pf_admin_id, coord_id, diana_instructor_id)
        )
        commit()
        print(f"✓ Ficha 3115419 (Admin Financiera) creada id={ficha_admin_id}")
    else:
        q("""UPDATE ficha_formacion
             SET id_instructor=%s, id_proyecto_formativo=%s
             WHERE id=%s""",
          (diana_instructor_id, pf_admin_id, ficha_admin_id))
        commit()
        print(f"✓ Ficha 3115419 (Admin Financiera) existente id={ficha_admin_id} (actualizada)")

    # ── 8. Fases, actividades de proyecto y guías de ejemplo ─────────────────
    def seed_fases(pf_id, fases_data, label):
        for fase_data in fases_data:
            fase_id = first(
                "SELECT id FROM fase_proyecto WHERE id_proyecto_formativo=%s AND nombre=%s",
                (pf_id, fase_data["nombre"])
            )
            if not fase_id:
                fase_id = first(
                    "INSERT INTO fase_proyecto (id_proyecto_formativo, nombre) VALUES (%s,%s) RETURNING id",
                    (pf_id, fase_data["nombre"])
                )
                commit()

            ap_id = first(
                "SELECT id FROM actividad_proyecto WHERE id_fase_proyecto=%s AND nombre=%s",
                (fase_id, fase_data["actividad_proyecto"])
            )
            if not ap_id:
                ap_id = first(
                    "INSERT INTO actividad_proyecto (id_fase_proyecto, nombre) VALUES (%s,%s) RETURNING id",
                    (fase_id, fase_data["actividad_proyecto"])
                )
                commit()

            # Guía de ejemplo en la nueva tabla guia_actividad_proyecto
            guia_exists = first(
                "SELECT id FROM guia_actividad_proyecto WHERE id_actividad_proyecto=%s AND nombre=%s",
                (ap_id, fase_data["guia_nombre"])
            )
            if not guia_exists:
                first(
                    """INSERT INTO guia_actividad_proyecto
                       (id_actividad_proyecto, nombre, url)
                       VALUES (%s,%s,%s) RETURNING id""",
                    (ap_id, fase_data["guia_nombre"], fase_data["guia_url"])
                )
                commit()

            print(f"  ✓ [{label}] {fase_data['nombre']} → {fase_data['actividad_proyecto']} + guía")

    print("\n── Fases ADSI ─────────────────────────────────────────────")
    seed_fases(pf_adsi_id, FASES_ADSI, "ADSI")

    print("\n── Fases Admin Financiera ─────────────────────────────────")
    seed_fases(pf_admin_id, FASES_ADMIN, "Admin")

    # ── 9. Aprendices ─────────────────────────────────────────────────────────
    def upsert_aprendiz(doc, nombres, apellidos, ficha_num):
        exists = first(
            "SELECT id FROM aprendiz WHERE documento=%s AND ficha=%s",
            (doc, ficha_num)
        )
        if not exists:
            first(
                """INSERT INTO aprendiz (id_regional, documento, nombres, apellidos, ficha)
                   VALUES (%s,%s,%s,%s,%s) RETURNING id""",
                (regional_id, doc, nombres, apellidos, ficha_num)
            )

    def upsert_usuario_aprendiz(doc, nombres, apellidos):
        email = f"aprendiz.{doc}@barilms.local"
        nombre_completo = f"{nombres} {apellidos}"
        exists = first("SELECT id FROM usuario WHERE lower(correo)=%s", (email.lower(),))
        if not exists:
            first(
                """INSERT INTO usuario (correo, contrasena_hash, rol, nombre, activo)
                   VALUES (%s,%s,%s,%s,%s) RETURNING id""",
                (email, generate_password_hash(doc), "Aprendiz", nombre_completo, True)
            )

    print("\n── Aprendices ─────────────────────────────────────────────")

    for doc, nombres, apellidos in COMPARTIDOS:
        upsert_aprendiz(doc, nombres, apellidos, "3115418")
        upsert_aprendiz(doc, nombres, apellidos, "3115419")
        upsert_usuario_aprendiz(doc, nombres, apellidos)
        print(f"  [ADSI + Admin] {nombres} {apellidos}")

    for doc, nombres, apellidos in SOLO_ADSI:
        upsert_aprendiz(doc, nombres, apellidos, "3115418")
        upsert_usuario_aprendiz(doc, nombres, apellidos)
        print(f"  [ADSI]         {nombres} {apellidos}")

    for doc, nombres, apellidos in SOLO_ADMIN:
        upsert_aprendiz(doc, nombres, apellidos, "3115419")
        upsert_usuario_aprendiz(doc, nombres, apellidos)
        print(f"  [Admin]        {nombres} {apellidos}")

    commit()
    conn.close()

    print()
    print("═" * 65)
    print("  RESUMEN")
    print("═" * 65)
    print("  Ficha 3115418 — Análisis y Desarrollo de Software (ADSI)")
    print("    Instructora : Diana Beltrán")
    print("    Aprendices  : 15 (5 compartidos + 10 exclusivos)")
    print("    Fases       : 4 — con 1 actividad de proyecto y 1 guía c/u")
    print()
    print("  Ficha 3115419 — Administración Financiera")
    print("    Instructora : Diana Beltrán")
    print("    Aprendices  : 15 (5 compartidos + 10 exclusivos)")
    print("    Fases       : 4 — con 1 actividad de proyecto y 1 guía c/u")
    print()
    print("  Login aprendices → aprendiz.<documento>@barilms.local")
    print("  Contraseña inicial → número de documento")
    print("═" * 65)
    print("✓ Seed completado.")


if __name__ == "__main__":
    run()
