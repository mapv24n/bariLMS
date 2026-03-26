import os
import sys
import psycopg

# Path resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
sys.path.insert(0, os.path.join(project_root, "internal"))

from bari_lms.services.security import hash_password
from data import DATA_INSTRUCTORES, SEED_PASSWORD, generate_id
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
    print("  → Hashing password and resolving dependencies...")
    pw_hash = hash_password(SEED_PASSWORD)
    
    # Resolve IDs once
    deps = {
        "tipo_doc": _resolve_id(cur, "tipo_documento", "codigo", "cc"),
        "sexo_m": _resolve_id(cur, "sexo", "codigo", "m"),
        "sexo_f": _resolve_id(cur, "sexo", "codigo", "f"),
        "centro": _resolve_id(cur, "centro", "nombre", "Centro de Gestión de Mercados, Logística y TIC del Norte de Santander"),
        "coord": _resolve_id(cur, "coordinacion", "nombre", "Coordinación de Tecnologías de la Información"),
        "area": _resolve_id(cur, "area", "nombre", "Análisis y Desarrollo de Software"),
        "proyecto": _resolve_id(cur, "proyecto_formativo", "codigo", "PF-ADSO-001"),
        "programa": _resolve_id(cur, "programa_formacion", "nombre", "Análisis y Desarrollo de Software"),
        "perfil": _resolve_id(cur, "perfil", "nombre", "Instructor")
    }

    for correo, nombre_full, doc, nom, ape, sex_cod, num_ficha in DATA_INSTRUCTORES:
        print(f"  → Instructor: {correo}")
        
        # 1. User (ID = Persona ID)
        u_id = generate_id()
        is_new = SeedQueries.INSERT_USUARIO.execute(cur, (u_id, correo, pw_hash, nombre_full))
        actual_u_id = _resolve_id(cur, "usuario", "correo", correo)

        # 2. Persona
        s_id = deps["sexo_m"] if sex_cod == "m" else deps["sexo_f"]
        SeedQueries.INSERT_PERSONA.execute(cur, (actual_u_id, deps["tipo_doc"], doc, nom, ape, s_id))

        # 3. Instructor Entity
        SeedQueries.INSERT_INSTRUCTOR.execute(cur, (generate_id(), actual_u_id, deps["centro"], deps["area"]))
        actual_inst_id = _resolve_id(cur, "instructor", "persona_id", actual_u_id)

        # 4. Profile Role
        if deps["perfil"]:
            SeedQueries.INSERT_PERFIL_LINK.execute(cur, (generate_id(), actual_u_id, deps["perfil"]))

        # 5. Ficha
        SeedQueries.INSERT_FICHA.execute(cur, (
            generate_id(), num_ficha, deps["programa"], deps["coord"], deps["proyecto"], actual_inst_id
        ))
        
        print(f"    {'[NEW]' if is_new else '[EXISTING]'} Processed successfully.")

if __name__ == "__main__":
    print("[ Seed 02 - Refactored ] Starting...")
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                run(cur)
            conn.commit()
        print("[ Seed 02 ] All tasks completed.\n")
    except Exception as e:
        print(f"[ Seed 02 ] Fatal Error: {e}")