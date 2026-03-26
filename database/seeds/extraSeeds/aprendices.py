import os
import sys
import psycopg

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
sys.path.insert(0, os.path.join(project_root, "internal"))

from bari_lms.services.security import hash_password
from data import DATA_APRENDICES, DATA_EMPRESAS, SEED_PASSWORD, generate_id
from queries import SeedQueries

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
    print("  → Resolving dependencies...")
    pw_hash = hash_password(SEED_PASSWORD)
    
    # Global dependencies
    deps = {
        "cc": _resolve_id(cur, "tipo_documento", "codigo", "cc"),
        "ti": _resolve_id(cur, "tipo_documento", "codigo", "ti"),
        "m": _resolve_id(cur, "sexo", "codigo", "m"),
        "f": _resolve_id(cur, "sexo", "codigo", "f"),
        "regional": _resolve_id(cur, "regional", "nombre", "Regional Antioquia"), # Adjust to your Regional
        "perfil": _resolve_id(cur, "perfil", "nombre", "Aprendiz")
    }

    # 1. Seed Companies
    print("  → Seeding companies...")
    for razon, nit, sector, correo, tel in DATA_EMPRESAS:
        SeedQueries.INSERT_EMPRESA.execute(cur, (generate_id(), razon, nit, sector, correo, tel))

    # 2. Seed Apprentices & Enrollments
    print("  → Seeding apprentices...")
    for correo, full_n, doc, t_doc, nom, ape, sex, f_num, lect, concl, prod in DATA_APRENDICES:
        print(f"    - Apprentice: {correo}")
        
        # A. User
        u_id = generate_id()
        SeedQueries.INSERT_USUARIO.execute(cur, (u_id, correo, pw_hash, full_n))
        actual_u_id = _resolve_id(cur, "usuario", "correo", correo)

        # B. Persona
        SeedQueries.INSERT_PERSONA.execute(cur, (
            actual_u_id, deps[t_doc], doc, nom, ape, deps[sex]
        ))

        # C. Aprendiz Entity
        SeedQueries.INSERT_APRENDIZ.execute(cur, (generate_id(), actual_u_id, deps["regional"]))
        actual_apr_id = _resolve_id(cur, "aprendiz", "persona_id", actual_u_id)

        # D. Profile Link
        if deps["perfil"]:
            SeedQueries.INSERT_PERFIL_LINK.execute(cur, (generate_id(), actual_u_id, deps["perfil"]))

        # E. Ficha Enrollment
        ficha_id = _resolve_id(cur, "ficha_formacion", "numero", f_num)
        if ficha_id:
            SeedQueries.INSERT_FICHA_APRENDIZ.execute(cur, (
                generate_id(), ficha_id, actual_apr_id, lect, concl, prod
            ))

if __name__ == "__main__":
    print("[ Seed 03 - Refactored ] Starting Apprentices & EP...")
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                run(cur)
            conn.commit()
        print("[ Seed 03 ] Success.\n")
    except Exception as e:
        print(f"[ Seed 03 ] Error: {e}")