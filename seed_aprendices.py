#!/usr/bin/env python3
"""
Seed: Biblioteca de aprendices para fichas 3115418 (ADSI) y 3115419 (Cocina).

Ejecutar: python seed_aprendices.py
Idempotente: se puede correr varias veces sin duplicar datos.
"""
import os
import sqlite3
from werkzeug.security import generate_password_hash

DB = os.path.join(os.path.dirname(__file__), "bari_lms.db")

# ── Biblioteca de aprendices ─────────────────────────────────────────────────
# (documento, nombres, apellidos, genero)
# Genero solo referencial aquí; en la tabla aprendiz no hay campo genero (solo usuario lo tiene).

COMPARTIDOS = [  # 5 aprendices en AMBAS fichas (programas distintos)
    ("1001001001", "Carlos",     "Mendoza García"),
    ("1001001002", "Laura",      "Jiménez Pérez"),
    ("1001001003", "Andrés",     "Morales Torres"),
    ("1001001004", "Valentina",  "Ríos Castillo"),
    ("1001001005", "Miguel",     "Torres Ruiz"),
]

SOLO_ADSI = [  # 5 aprendices exclusivos ficha ADSI 3115418
    ("1001001006", "Sebastián",  "Gómez López"),
    ("1001001007", "Isabella",   "Vargas Montoya"),
    ("1001001008", "Daniel",     "Herrera Sánchez"),
    ("1001001009", "Camila",     "Ospina Restrepo"),
    ("1001001010", "Santiago",   "Reyes Méndez"),
]

SOLO_COCINA = [  # 5 aprendices exclusivos ficha Cocina 3115419
    ("1001001011", "Gabriela",   "Suárez Vega"),
    ("1001001012", "Felipe",     "Castro Díaz"),
    ("1001001013", "Natalia",    "Ramos Ortega"),
    ("1001001014", "Julián",     "Peña Vargas"),
    ("1001001015", "María José", "Rojas Fuentes"),
]

# ── Fases y actividades para cada proyecto formativo ────────────────────────
FASES_ADSI = [
    {
        "nombre": "Fase 1: Direccionamiento",
        "actividades_proyecto": [
            {
                "nombre": "Análisis de Requisitos",
                "actividades_aprendizaje": [
                    "Levantamiento de información del cliente",
                    "Definición del alcance del proyecto",
                ],
            }
        ],
    },
    {
        "nombre": "Fase 2: Planeación",
        "actividades_proyecto": [
            {
                "nombre": "Diseño de la Solución",
                "actividades_aprendizaje": [
                    "Modelado de base de datos",
                    "Diseño de arquitectura del sistema",
                ],
            }
        ],
    },
    {
        "nombre": "Fase 3: Ejecución",
        "actividades_proyecto": [
            {
                "nombre": "Desarrollo del Software",
                "actividades_aprendizaje": [
                    "Implementación del módulo principal",
                    "Pruebas unitarias y de integración",
                ],
            }
        ],
    },
    {
        "nombre": "Fase 4: Socialización",
        "actividades_proyecto": [
            {
                "nombre": "Entrega del Producto",
                "actividades_aprendizaje": [
                    "Presentación del proyecto ante el cliente",
                ],
            }
        ],
    },
]

FASES_COCINA = [
    {
        "nombre": "Fase 1: Direccionamiento",
        "actividades_proyecto": [
            {
                "nombre": "Exploración Gastronómica",
                "actividades_aprendizaje": [
                    "Identificación de recetas regionales",
                    "Historia y cultura de la gastronomía local",
                ],
            }
        ],
    },
    {
        "nombre": "Fase 2: Planeación",
        "actividades_proyecto": [
            {
                "nombre": "Planificación del Menú",
                "actividades_aprendizaje": [
                    "Elaboración de menú temático",
                    "Costeo y presupuesto de ingredientes",
                ],
            }
        ],
    },
    {
        "nombre": "Fase 3: Ejecución",
        "actividades_proyecto": [
            {
                "nombre": "Preparación Culinaria",
                "actividades_aprendizaje": [
                    "Técnicas de cocción aplicadas",
                    "Manejo de BPM en cocina",
                ],
            }
        ],
    },
    {
        "nombre": "Fase 4: Socialización",
        "actividades_proyecto": [
            {
                "nombre": "Muestra Gastronómica",
                "actividades_aprendizaje": [
                    "Presentación y montaje de platos",
                ],
            }
        ],
    },
]


def run():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    def q(sql, params=()):
        return conn.execute(sql, params)

    def first(sql, params=()):
        r = q(sql, params).fetchone()
        return r[0] if r else None

    print("═" * 60)
    print("  SEED: Fichas ADSI 3115418 y Cocina 3115419")
    print("═" * 60)

    # ── Datos base ya existentes ──────────────────────────────────
    coordinacion_id = first("SELECT id FROM coordinacion LIMIT 1")
    if not coordinacion_id:
        raise RuntimeError("No hay ninguna coordinación en la BD. Crea una desde admin_structure primero.")
    print(f"✓ Usando coordinación id={coordinacion_id}")

    nivel_tecnologo_id = first("SELECT id FROM nivel_formacion WHERE nombre LIKE '%ecn%logo%'")
    nivel_tecnico_id   = first("SELECT id FROM nivel_formacion WHERE nombre LIKE '%écnico%' AND nombre NOT LIKE '%ecn%logo%'")
    if not nivel_tecnologo_id:
        nivel_tecnologo_id = first("SELECT id FROM nivel_formacion ORDER BY id LIMIT 1")
    if not nivel_tecnico_id:
        nivel_tecnico_id = nivel_tecnologo_id
    print(f"✓ Nivel Tecnólogo id={nivel_tecnologo_id} | Nivel Técnico id={nivel_tecnico_id}")

    # ── Redes de conocimiento ─────────────────────────────────────
    red_ti_id = first("SELECT id FROM red_conocimiento WHERE nombre = ?", ("Tecnología de la Información",))
    if not red_ti_id:
        red_ti_id = q("INSERT INTO red_conocimiento (nombre) VALUES (?)", ("Tecnología de la Información",)).lastrowid
        conn.commit()
        print("✓ Red 'Tecnología de la Información' creada")
    else:
        print(f"✓ Red TI ya existe id={red_ti_id}")

    red_serv_id = first("SELECT id FROM red_conocimiento WHERE nombre = ?", ("Servicios Personales y Sociales",))
    if not red_serv_id:
        red_serv_id = q("INSERT INTO red_conocimiento (nombre) VALUES (?)", ("Servicios Personales y Sociales",)).lastrowid
        conn.commit()
        print("✓ Red 'Servicios Personales y Sociales' creada")
    else:
        print(f"✓ Red Servicios ya existe id={red_serv_id}")

    # ── Áreas académicas ──────────────────────────────────────────
    area_soft_id = first("SELECT id FROM area WHERE nombre = ? AND id_red_conocimiento = ?",
                         ("Desarrollo de Software", red_ti_id))
    if not area_soft_id:
        area_soft_id = q("INSERT INTO area (id_red_conocimiento, nombre) VALUES (?,?)",
                         (red_ti_id, "Desarrollo de Software")).lastrowid
        conn.commit()
        print("✓ Área 'Desarrollo de Software' creada")
    else:
        print(f"✓ Área Software ya existe id={area_soft_id}")

    area_cocina_id = first("SELECT id FROM area WHERE nombre = ? AND id_red_conocimiento = ?",
                           ("Gastronomía", red_serv_id))
    if not area_cocina_id:
        area_cocina_id = q("INSERT INTO area (id_red_conocimiento, nombre) VALUES (?,?)",
                           (red_serv_id, "Gastronomía")).lastrowid
        conn.commit()
        print("✓ Área 'Gastronomía' creada")
    else:
        print(f"✓ Área Gastronomía ya existe id={area_cocina_id}")

    # ── Programas de formación ─────────────────────────────────────
    prog_adsi_id = first("SELECT id FROM programa_formacion WHERE nombre = ?",
                         ("Análisis y Desarrollo de Software",))
    if not prog_adsi_id:
        prog_adsi_id = q("INSERT INTO programa_formacion (id_area, id_nivel_formacion, nombre) VALUES (?,?,?)",
                         (area_soft_id, nivel_tecnologo_id, "Análisis y Desarrollo de Software")).lastrowid
        conn.commit()
        print("✓ Programa 'Análisis y Desarrollo de Software' creado")
    else:
        print(f"✓ Programa ADSI ya existe id={prog_adsi_id}")

    prog_cocina_id = first("SELECT id FROM programa_formacion WHERE nombre = ?",
                           ("Técnico en Cocina",))
    if not prog_cocina_id:
        prog_cocina_id = q("INSERT INTO programa_formacion (id_area, id_nivel_formacion, nombre) VALUES (?,?,?)",
                           (area_cocina_id, nivel_tecnico_id, "Técnico en Cocina")).lastrowid
        conn.commit()
        print("✓ Programa 'Técnico en Cocina' creado")
    else:
        print(f"✓ Programa Cocina ya existe id={prog_cocina_id}")

    # ── Proyectos formativos ──────────────────────────────────────
    pf_adsi_id = first("SELECT id FROM proyecto_formativo WHERE codigo = ?", ("PF-ADSI-2025",))
    if not pf_adsi_id:
        pf_adsi_id = q("INSERT INTO proyecto_formativo (codigo, nombre) VALUES (?,?)",
                       ("PF-ADSI-2025", "Desarrollo de Soluciones de Software a la Medida")).lastrowid
        conn.commit()
        print("✓ Proyecto formativo ADSI creado")
    else:
        print(f"✓ PF ADSI ya existe id={pf_adsi_id}")

    pf_cocina_id = first("SELECT id FROM proyecto_formativo WHERE codigo = ?", ("PF-COC-2025",))
    if not pf_cocina_id:
        pf_cocina_id = q("INSERT INTO proyecto_formativo (codigo, nombre) VALUES (?,?)",
                         ("PF-COC-2025", "Producción Gastronómica Tradicional Colombiana")).lastrowid
        conn.commit()
        print("✓ Proyecto formativo Cocina creado")
    else:
        print(f"✓ PF Cocina ya existe id={pf_cocina_id}")

    # ── Fases y actividades de ADSI ───────────────────────────────
    def seed_fases(proyecto_id, fases_data):
        for fase_data in fases_data:
            fase_id = first("SELECT id FROM fase_proyecto WHERE id_proyecto_formativo=? AND nombre=?",
                            (proyecto_id, fase_data["nombre"]))
            if not fase_id:
                fase_id = q("INSERT INTO fase_proyecto (id_proyecto_formativo, nombre) VALUES (?,?)",
                            (proyecto_id, fase_data["nombre"])).lastrowid
                conn.commit()
            for ap_data in fase_data["actividades_proyecto"]:
                ap_id = first("SELECT id FROM actividad_proyecto WHERE id_fase_proyecto=? AND nombre=?",
                              (fase_id, ap_data["nombre"]))
                if not ap_id:
                    ap_id = q("INSERT INTO actividad_proyecto (id_fase_proyecto, nombre) VALUES (?,?)",
                              (fase_id, ap_data["nombre"])).lastrowid
                    conn.commit()
                for aa_nombre in ap_data["actividades_aprendizaje"]:
                    aa_exists = first("SELECT id FROM actividad_aprendizaje WHERE id_actividad_proyecto=? AND nombre=?",
                                     (ap_id, aa_nombre))
                    if not aa_exists:
                        q("INSERT INTO actividad_aprendizaje (id_actividad_proyecto, nombre) VALUES (?,?)",
                          (ap_id, aa_nombre))
                        conn.commit()

    seed_fases(pf_adsi_id, FASES_ADSI)
    print("✓ Fases y actividades ADSI creadas")

    seed_fases(pf_cocina_id, FASES_COCINA)
    print("✓ Fases y actividades Cocina creadas")

    # ── Instructor Diana Beltran ──────────────────────────────────
    diana_usuario_id = first("SELECT id FROM usuario WHERE lower(correo) = ?",
                             ("instructor@senalearn.edu.co",))
    diana_instructor_id = None
    if diana_usuario_id:
        diana_instructor_id = first("SELECT id FROM instructor WHERE id_usuario = ?", (diana_usuario_id,))
        if not diana_instructor_id:
            diana_instructor_id = q(
                """INSERT INTO instructor
                   (id_coordinacion, id_area, documento, nombres, apellidos,
                    correo, id_usuario, genero)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (coordinacion_id, area_soft_id, "52987654",
                 "Diana", "Beltran",
                 "instructor@senalearn.edu.co", diana_usuario_id, "F")
            ).lastrowid
            conn.commit()
            print(f"✓ Registro instructor Diana Beltran creado id={diana_instructor_id}")
        else:
            # Asegurar que tiene area_soft asignada
            q("UPDATE instructor SET id_area=?, genero='F' WHERE id=?",
              (area_soft_id, diana_instructor_id))
            conn.commit()
            print(f"✓ Instructor Diana Beltran ya existe id={diana_instructor_id} (actualizado área y género)")
    else:
        print("⚠ No se encontró usuario instructor@senalearn.edu.co — la ficha ADSI queda sin instructor")

    # ── Fichas de formación ───────────────────────────────────────
    ficha_adsi_id = first("SELECT id FROM ficha_formacion WHERE numero = ?", ("3115418",))
    if not ficha_adsi_id:
        ficha_adsi_id = q(
            """INSERT INTO ficha_formacion
               (numero, id_programa_formacion, id_proyecto_formativo,
                id_coordinacion, id_instructor)
               VALUES (?,?,?,?,?)""",
            ("3115418", prog_adsi_id, pf_adsi_id, coordinacion_id, diana_instructor_id)
        ).lastrowid
        conn.commit()
        print(f"✓ Ficha ADSI 3115418 creada (instructora: Diana Beltran)")
    else:
        if diana_instructor_id:
            q("UPDATE ficha_formacion SET id_instructor=?, id_proyecto_formativo=? WHERE id=?",
              (diana_instructor_id, pf_adsi_id, ficha_adsi_id))
            conn.commit()
        print(f"✓ Ficha ADSI 3115418 ya existe id={ficha_adsi_id} (instructor actualizado)")

    ficha_cocina_id = first("SELECT id FROM ficha_formacion WHERE numero = ?", ("3115419",))
    if not ficha_cocina_id:
        ficha_cocina_id = q(
            """INSERT INTO ficha_formacion
               (numero, id_programa_formacion, id_proyecto_formativo,
                id_coordinacion, id_instructor)
               VALUES (?,?,?,?,?)""",
            ("3115419", prog_cocina_id, pf_cocina_id, coordinacion_id, None)
        ).lastrowid
        conn.commit()
        print(f"✓ Ficha Cocina 3115419 creada (sin instructor asignado)")
    else:
        print(f"✓ Ficha Cocina 3115419 ya existe id={ficha_cocina_id}")

    # ── Insertar aprendices ───────────────────────────────────────
    def insert_aprendiz_ficha(doc, nombres, apellidos, ficha_num):
        exists = first(
            "SELECT id FROM aprendiz WHERE documento=? AND ficha=?",
            (doc, ficha_num)
        )
        if not exists:
            q("INSERT INTO aprendiz (id_coordinacion, documento, nombres, apellidos, ficha) VALUES (?,?,?,?,?)",
              (coordinacion_id, doc, nombres, apellidos, ficha_num))

    def insert_usuario_aprendiz(doc, nombres, apellidos):
        email = f"aprendiz.{doc}@barilms.local"
        nombre_completo = f"{nombres} {apellidos}"
        exists = first("SELECT id FROM usuario WHERE lower(correo)=?", (email.lower(),))
        if not exists:
            q("INSERT INTO usuario (correo, contrasena_hash, rol, nombre, activo) VALUES (?,?,?,?,?)",
              (email, generate_password_hash(doc), "Aprendiz", nombre_completo, 1))

    print()
    print("── Insertando aprendices ──────────────────────────────")

    # 5 compartidos → aparecen en las dos fichas (programas distintos)
    for doc, nombres, apellidos in COMPARTIDOS:
        insert_aprendiz_ficha(doc, nombres, apellidos, "3115418")
        insert_aprendiz_ficha(doc, nombres, apellidos, "3115419")
        insert_usuario_aprendiz(doc, nombres, apellidos)
        print(f"  [ADSI + Cocina] {nombres} {apellidos}")

    # 5 exclusivos ADSI
    for doc, nombres, apellidos in SOLO_ADSI:
        insert_aprendiz_ficha(doc, nombres, apellidos, "3115418")
        insert_usuario_aprendiz(doc, nombres, apellidos)
        print(f"  [ADSI]          {nombres} {apellidos}")

    # 5 exclusivos Cocina
    for doc, nombres, apellidos in SOLO_COCINA:
        insert_aprendiz_ficha(doc, nombres, apellidos, "3115419")
        insert_usuario_aprendiz(doc, nombres, apellidos)
        print(f"  [Cocina]        {nombres} {apellidos}")

    conn.commit()
    conn.close()

    print()
    print("═" * 60)
    print("  RESUMEN")
    print("═" * 60)
    print("  Ficha 3115418 — Análisis y Desarrollo de Software")
    print("    Instructora líder : Diana Beltran")
    print("    Aprendices        : 10 (5 compartidos + 5 exclusivos)")
    print()
    print("  Ficha 3115419 — Técnico en Cocina")
    print("    Instructor líder  : (sin asignar)")
    print("    Aprendices        : 10 (5 compartidos + 5 exclusivos)")
    print()
    print("  5 aprendices en ambas fichas (programas distintos):")
    for _, n, a in COMPARTIDOS:
        print(f"    • {n} {a}")
    print()
    print("  Acceso aprendices → correo: aprendiz.<documento>@barilms.local")
    print("  Contraseña inicial         → número de documento")
    print("═" * 60)
    print("✓ Seed completado exitosamente.")


if __name__ == "__main__":
    run()
