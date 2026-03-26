"""
Proyecto    : bariLMS — Sistema de Gestión del Aprendizaje (SENA)
Archivo     : database/seed_test_data.py
Descripción : Datos de prueba para desarrollo local.
              Completa los registros de persona, instructor, aprendiz y
              personal_administrativo para los usuarios de prueba existentes.
              También crea estructura mínima (regional, centro, coordinacion,
              red_conocimiento, area) requerida como FK.

Uso:
    python database/seed_test_data.py

Requiere .env con PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD.
Es seguro re-ejecutar: todo usa ON CONFLICT DO NOTHING.
"""

import os
import uuid

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_conn():
    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=int(os.environ.get("PGPORT", 5432)),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ.get("PGPASSWORD", ""),
    )


def uid() -> str:
    return str(uuid.uuid7())


def seed_test_data(conn):
    with conn.cursor() as cur:

        # ── 1. Estructura institucional mínima ───────────────────────────────

        regional_id = uid()
        cur.execute(
            "INSERT INTO regional (id, nombre) VALUES (%s, %s) "
            "ON CONFLICT (nombre) DO NOTHING",
            (regional_id, "Regional Bogotá - Cundinamarca"),
        )
        cur.execute(
            "SELECT id FROM regional WHERE nombre = %s",
            ("Regional Bogotá - Cundinamarca",),
        )
        regional_id = cur.fetchone()[0]

        centro_id = uid()
        cur.execute(
            "INSERT INTO centro (id, regional_id, nombre) VALUES (%s, %s, %s) "
            "ON CONFLICT DO NOTHING",
            (centro_id, regional_id, "Centro de Servicios Financieros"),
        )
        cur.execute(
            "SELECT id FROM centro WHERE nombre = %s AND regional_id = %s",
            ("Centro de Servicios Financieros", regional_id),
        )
        centro_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO coordinacion (id, centro_id, nombre) VALUES (%s, %s, %s) "
            "ON CONFLICT DO NOTHING",
            (uid(), centro_id, "Coordinación Académica"),
        )

        red_id = uid()
        cur.execute(
            "INSERT INTO red_conocimiento (id, nombre) VALUES (%s, %s) "
            "ON CONFLICT (nombre) DO NOTHING",
            (red_id, "Red de Sistemas y Telecomunicaciones"),
        )
        cur.execute(
            "SELECT id FROM red_conocimiento WHERE nombre = %s",
            ("Red de Sistemas y Telecomunicaciones",),
        )
        red_id = cur.fetchone()[0]

        area_id = uid()
        cur.execute(
            "INSERT INTO area (id, red_conocimiento_id, nombre) VALUES (%s, %s, %s) "
            "ON CONFLICT DO NOTHING",
            (area_id, red_id, "Área de Análisis y Desarrollo de Software"),
        )
        cur.execute(
            "SELECT id FROM area WHERE nombre = %s AND red_conocimiento_id = %s",
            ("Área de Análisis y Desarrollo de Software", red_id),
        )
        area_id = cur.fetchone()[0]

        print("  [OK] Estructura institucional")

        # ── 2. Recuperar IDs de usuarios de prueba ───────────────────────────

        cur.execute(
            "SELECT id FROM usuario WHERE correo_institucional = %s",
            ("instructor@senalearn.edu.co",),
        )
        row = cur.fetchone()
        if row is None:
            print("  [OMITIDO] instructor@senalearn.edu.co no existe en usuario")
            instructor_user_id = None
        else:
            instructor_user_id = row[0]

        cur.execute(
            "SELECT id FROM usuario WHERE correo_institucional = %s",
            ("aprendiz@senalearn.edu.co",),
        )
        row = cur.fetchone()
        if row is None:
            print("  [OMITIDO] aprendiz@senalearn.edu.co no existe en usuario")
            aprendiz_user_id = None
        else:
            aprendiz_user_id = row[0]

        cur.execute(
            "SELECT id FROM usuario WHERE correo_institucional = %s",
            ("administrativo@senalearn.edu.co",),
        )
        row = cur.fetchone()
        if row is None:
            print("  [OMITIDO] administrativo@senalearn.edu.co no existe en usuario")
            admin_user_id = None
        else:
            admin_user_id = row[0]

        # ── 3. Instructor ────────────────────────────────────────────────────

        if instructor_user_id:
            cur.execute(
                "INSERT INTO persona (id, nombres, apellidos, numero_documento) "
                "VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                (instructor_user_id, "INSTRUCTOR", "DE PRUEBA", "11111111"),
            )
            cur.execute(
                "INSERT INTO instructor (id, persona_id, centro_id, area_id) "
                "VALUES (%s, %s, %s, %s) ON CONFLICT (persona_id) DO NOTHING",
                (uid(), instructor_user_id, centro_id, area_id),
            )
            print("  [OK] instructor@senalearn.edu.co: persona + instructor")

        # ── 4. Aprendiz ──────────────────────────────────────────────────────

        if aprendiz_user_id:
            cur.execute(
                "INSERT INTO persona (id, nombres, apellidos, numero_documento) "
                "VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                (aprendiz_user_id, "APRENDIZ", "DE PRUEBA", "22222222"),
            )
            cur.execute(
                "INSERT INTO aprendiz (id, persona_id, regional_id) "
                "VALUES (%s, %s, %s) ON CONFLICT (persona_id) DO NOTHING",
                (uid(), aprendiz_user_id, regional_id),
            )
            print("  [OK] aprendiz@senalearn.edu.co: persona + aprendiz")

        # ── 5. Personal administrativo ───────────────────────────────────────

        if admin_user_id:
            cur.execute(
                "INSERT INTO persona (id, nombres, apellidos, numero_documento) "
                "VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                (admin_user_id, "ADMINISTRATIVO", "DE PRUEBA", "33333333"),
            )
            cur.execute(
                "INSERT INTO personal_administrativo (id, persona_id, centro_id, cargo) "
                "VALUES (%s, %s, %s, %s) ON CONFLICT (persona_id) DO NOTHING",
                (uid(), admin_user_id, centro_id, "Apoyo Académico"),
            )
            print("  [OK] administrativo@senalearn.edu.co: persona + personal_administrativo")

    conn.commit()
    print("\nSeed de datos de prueba completado.")


if __name__ == "__main__":
    with get_conn() as conn:
        seed_test_data(conn)
