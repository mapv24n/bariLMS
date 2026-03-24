"""
Proyecto    : bariLMS
Archivo     : database/seed_aprendices_3115418.py
Descripcion : Crea 14 aprendices de prueba para la ficha 3115418.

              Por cada aprendiz genera:
                - usuario  (correo_institucional, contrasena_hash, activo=True)
                - persona  (id = usuario.id, nombres, apellidos, numero_documento)
                - aprendiz (persona_id, regional_id, ficha='3115418')
                - usuario_perfil -> perfil "Aprendiz"

              Contrasena por defecto: Aprendiz2025*
              Correos: aprendiz01@senalearn.edu.co ... aprendiz14@senalearn.edu.co

Uso:
    python database/seed_aprendices_3115418.py

Requiere .env con PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD.
Es seguro re-ejecutar: todo usa ON CONFLICT DO NOTHING.
"""

import os
import uuid

import psycopg
from argon2 import PasswordHasher
from dotenv import load_dotenv

load_dotenv()

FICHA = "3115418"
PASSWORD = "Aprendiz2025*"

APRENDICES = [
    ("CARLOS ANDRES",  "MARTINEZ LOPEZ",   "1000001"),
    ("MARIA FERNANDA", "GARCIA TORRES",    "1000002"),
    ("JUAN PABLO",     "RODRIGUEZ HERRERA","1000003"),
    ("ANA LUCIA",      "SANCHEZ MORALES",  "1000004"),
    ("DIEGO ALEJANDRO","VARGAS JIMENEZ",   "1000005"),
    ("LAURA CAMILA",   "GOMEZ CASTILLO",   "1000006"),
    ("ANDRES FELIPE",  "DIAZ ROJAS",       "1000007"),
    ("VALENTINA",      "RIOS MENDOZA",     "1000008"),
    ("SANTIAGO",       "PEREZ ACOSTA",     "1000009"),
    ("ISABELLA",       "RAMIREZ SILVA",    "1000010"),
    ("NICOLAS",        "MORA GUERRERO",    "1000011"),
    ("DANIELA",        "FLOREZ CAMPOS",    "1000012"),
    ("SEBASTIAN",      "CRUZ NAVARRO",     "1000013"),
    ("CAMILA ANDREA",  "LEON OSPINA",      "1000014"),
]


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


def seed_aprendices(conn):
    ph = PasswordHasher()
    password_hash = ph.hash(PASSWORD)

    with conn.cursor() as cur:

        # Obtener regional_id (cualquiera existente)
        cur.execute("SELECT id FROM regional LIMIT 1")
        row = cur.fetchone()
        if row is None:
            print("[ERROR] No hay regionales en la BD. Ejecuta seed_test_data.py primero.")
            return
        regional_id = row[0]

        # Obtener perfil_id de "Aprendiz"
        cur.execute("SELECT id FROM perfil WHERE nombre = 'Aprendiz'")
        row = cur.fetchone()
        if row is None:
            print("[ERROR] No existe el perfil 'Aprendiz'. Ejecuta seed.py primero.")
            return
        perfil_id = row[0]

        print(f"  Regional : {regional_id}")
        print(f"  Perfil   : {perfil_id}")
        print(f"  Ficha    : {FICHA}")
        print()

        for i, (nombres, apellidos, documento) in enumerate(APRENDICES, start=1):
            correo = f"aprendiz{i:02d}@senalearn.edu.co"

            # 1. usuario
            user_id = uid()
            cur.execute(
                "INSERT INTO usuario (id, correo_institucional, contrasena_hash, activo) "
                "VALUES (%s, %s, %s, %s) ON CONFLICT (correo_institucional) DO NOTHING",
                (user_id, correo, password_hash, True),
            )
            # Recuperar id real (por si ya existia)
            cur.execute(
                "SELECT id FROM usuario WHERE correo_institucional = %s", (correo,)
            )
            user_id = cur.fetchone()[0]

            # 2. persona
            cur.execute(
                "INSERT INTO persona (id, nombres, apellidos, numero_documento) "
                "VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                (user_id, nombres, apellidos, documento),
            )

            # 3. aprendiz
            cur.execute(
                "INSERT INTO aprendiz (id, persona_id, regional_id, ficha) "
                "VALUES (%s, %s, %s, %s) ON CONFLICT (persona_id) DO NOTHING",
                (uid(), user_id, regional_id, FICHA),
            )

            # 4. usuario_perfil
            cur.execute(
                "INSERT INTO usuario_perfil (id, usuario_id, perfil_id) "
                "VALUES (%s, %s, %s) ON CONFLICT (usuario_id, perfil_id) DO NOTHING",
                (uid(), user_id, perfil_id),
            )

            print(f"  [OK] {correo}  {nombres} {apellidos}")

    conn.commit()
    print(f"\n14 aprendices creados para ficha {FICHA}.")
    print(f"Contrasena de todos: {PASSWORD}")


if __name__ == "__main__":
    with get_conn() as conn:
        seed_aprendices(conn)
