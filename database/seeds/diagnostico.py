"""
Diagnóstico: verifica que la cadena usuario → instructor → ficha funcione.

Ejecutar desde la raíz del proyecto:
    python database/seeds/diagnostico.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "internal"))

import psycopg  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402

EMAILS_INSTRUCTOR = [
    "juan.perez@sena.edu.co",
    "maria.lopez@sena.edu.co",
    "carlos.rodriguez@sena.edu.co",
]


def connect():
    return psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE", "bari_lms"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", ""),
        row_factory=dict_row,
    )


def check(cur, label, query, params=()):
    cur.execute(query, params)
    rows = cur.fetchall()
    status = "✓" if rows else "✗ SIN RESULTADOS"
    print(f"  [{status}] {label}")
    for r in rows:
        print(f"           {dict(r)}")
    return rows


def main():
    with connect() as conn:
        with conn.cursor() as cur:

            print("\n══════════════════════════════════════════")
            print("  1. perfil 'Instructor' existe")
            print("══════════════════════════════════════════")
            check(cur, "perfil Instructor", "SELECT id, nombre FROM perfil WHERE nombre = 'Instructor'")

            for email in EMAILS_INSTRUCTOR:
                print(f"\n══════════════════════════════════════════")
                print(f"  Instructor: {email}")
                print(f"══════════════════════════════════════════")

                # Paso 1: usuario existe
                rows = check(cur, "usuario",
                    "SELECT id, correo, activo FROM usuario WHERE correo = %s", (email,))
                if not rows:
                    continue
                usuario_id = rows[0]["id"]

                # Paso 2: tiene perfil Instructor
                check(cur, "usuario_perfil",
                    """
                    SELECT up.usuario_id, p.nombre AS perfil
                    FROM usuario_perfil up
                    JOIN perfil p ON p.id = up.perfil_id
                    WHERE up.usuario_id = %s AND p.nombre = 'Instructor'
                    """, (usuario_id,))

                # Paso 3: persona existe con mismo UUID
                check(cur, "persona",
                    "SELECT id, nombres, apellidos FROM persona WHERE id = %s", (usuario_id,))

                # Paso 4: instructor con persona_id = usuario_id
                rows = check(cur, "instructor",
                    "SELECT id, persona_id, centro_id FROM instructor WHERE persona_id = %s",
                    (usuario_id,))
                if not rows:
                    continue
                instructor_id = rows[0]["id"]

                # Paso 5: fichas asignadas al instructor
                check(cur, "ficha_formacion",
                    """
                    SELECT f.id, f.numero, f.instructor_id,
                           p.nombre AS programa
                    FROM ficha_formacion f
                    JOIN programa_formacion p ON p.id = f.programa_formacion_id
                    WHERE f.instructor_id = %s
                    """, (instructor_id,))


if __name__ == "__main__":
    main()
    print()
