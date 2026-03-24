"""
Seed 03 — Aprendices, inscripciones y empresas EP.

Depende de: 01_estructura.py y 02_instructores.py.

Crea 6 aprendices (2 por ficha) con variedad de estados:
    Ficha 2900001 (Juan Pérez):
        apr1 → en etapa lectiva
        apr2 → lectiva concluida, en etapa productiva → TechSoft SAS

    Ficha 2900002 (María López):
        apr3 → en etapa lectiva
        apr4 → lectiva concluida, en etapa productiva → Innovatech Ltda

    Ficha 2900003 (Carlos Rodríguez):
        apr5 → en etapa lectiva
        apr6 → lectiva concluida, pendiente de empresa EP

Credenciales (perfil: Aprendiz):
    ana.gomez@aprendiz.sena.edu.co      / Sena2024*
    luis.torres@aprendiz.sena.edu.co    / Sena2024*
    sofia.mendez@aprendiz.sena.edu.co   / Sena2024*
    andres.ruiz@aprendiz.sena.edu.co    / Sena2024*
    camila.vargas@aprendiz.sena.edu.co  / Sena2024*
    miguel.castro@aprendiz.sena.edu.co  / Sena2024*

Ejecutar desde la raíz del proyecto:
    python database/seeds/03_aprendices.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "internal"))

import psycopg  # noqa: E402
from bari_lms.services.security import hash_password  # noqa: E402

USR_APR1 = "c1000000-0000-0000-0000-000000000001"
USR_APR2 = "c1000000-0000-0000-0000-000000000002"
USR_APR3 = "c1000000-0000-0000-0000-000000000003"
USR_APR4 = "c1000000-0000-0000-0000-000000000004"
USR_APR5 = "c1000000-0000-0000-0000-000000000005"
USR_APR6 = "c1000000-0000-0000-0000-000000000006"

APR1 = "c2000000-0000-0000-0000-000000000001"
APR2 = "c2000000-0000-0000-0000-000000000002"
APR3 = "c2000000-0000-0000-0000-000000000003"
APR4 = "c2000000-0000-0000-0000-000000000004"
APR5 = "c2000000-0000-0000-0000-000000000005"
APR6 = "c2000000-0000-0000-0000-000000000006"

EMP1 = "c3000000-0000-0000-0000-000000000001"
EMP2 = "c3000000-0000-0000-0000-000000000002"

FA1 = "c4000000-0000-0000-0000-000000000001"
FA2 = "c4000000-0000-0000-0000-000000000002"
FA3 = "c4000000-0000-0000-0000-000000000003"
FA4 = "c4000000-0000-0000-0000-000000000004"
FA5 = "c4000000-0000-0000-0000-000000000005"
FA6 = "c4000000-0000-0000-0000-000000000006"

# Empresa IDs kept here so the seed creates the catalog entries.
# The actual company ↔ aprendiz link lives in contrato_aprendizaje
# (see database/seeds_etapa_productiva/01_contratos.py).

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

    # ── Resolver IDs reales de seeds anteriores ───────────────────────────────
    tipo_doc_cc = _resolve_id(cur, "tipo_documento", "codigo", "cc")
    tipo_doc_ti = _resolve_id(cur, "tipo_documento", "codigo", "ti")
    sexo_m      = _resolve_id(cur, "sexo", "codigo", "m")
    sexo_f      = _resolve_id(cur, "sexo", "codigo", "f")
    regional_id = _resolve_id(cur, "regional", "nombre", "Regional Norte de Santander")
    ficha1      = _resolve_id(cur, "ficha_formacion", "numero", "2900001")
    ficha2      = _resolve_id(cur, "ficha_formacion", "numero", "2900002")
    ficha3      = _resolve_id(cur, "ficha_formacion", "numero", "2900003")

    # ── Usuarios aprendices ───────────────────────────────────────────────────
    print("  → usuario (aprendices)...")
    aprendices_usr = [
        (USR_APR1, "ana.gomez@aprendiz.sena.edu.co",     pw_hash, "Ana Sofía Gómez Herrera"),
        (USR_APR2, "luis.torres@aprendiz.sena.edu.co",   pw_hash, "Luis Eduardo Torres Prado"),
        (USR_APR3, "sofia.mendez@aprendiz.sena.edu.co",  pw_hash, "Sofía Alejandra Méndez Ríos"),
        (USR_APR4, "andres.ruiz@aprendiz.sena.edu.co",   pw_hash, "Andrés Felipe Ruiz Castillo"),
        (USR_APR5, "camila.vargas@aprendiz.sena.edu.co", pw_hash, "Camila Andrea Vargas Soto"),
        (USR_APR6, "miguel.castro@aprendiz.sena.edu.co", pw_hash, "Miguel Ángel Castro Jiménez"),
    ]
    for row in aprendices_usr:
        cur.execute(
            "INSERT INTO usuario (id, correo, contrasena_hash, nombre, activo)"
            " VALUES (%s, %s, %s, %s, TRUE) ON CONFLICT DO NOTHING",
            row,
        )
    # Resolver UUIDs reales (el correo es único → garantizado)
    usr_apr = [
        _resolve_id(cur, "usuario", "correo", correo)
        for _, correo, _, _ in aprendices_usr
    ]

    # ── Personas ──────────────────────────────────────────────────────────────
    print("  → persona (aprendices)...")
    personas = [
        (usr_apr[0], tipo_doc_cc, "1090123456", "ANA SOFÍA",       "GÓMEZ HERRERA",   sexo_f),
        (usr_apr[1], tipo_doc_cc, "1090234567", "LUIS EDUARDO",    "TORRES PRADO",    sexo_m),
        (usr_apr[2], tipo_doc_ti, "1025345678", "SOFÍA ALEJANDRA", "MÉNDEZ RÍOS",     sexo_f),
        (usr_apr[3], tipo_doc_ti, "1025456789", "ANDRÉS FELIPE",   "RUIZ CASTILLO",   sexo_m),
        (usr_apr[4], tipo_doc_cc, "1090567890", "CAMILA ANDREA",   "VARGAS SOTO",     sexo_f),
        (usr_apr[5], tipo_doc_cc, "1090678901", "MIGUEL ÁNGEL",    "CASTRO JIMÉNEZ",  sexo_m),
    ]
    for row in personas:
        cur.execute(
            "INSERT INTO persona (id, tipo_documento_id, numero_documento, nombres, apellidos, sexo_id)"
            " VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            row,
        )

    # ── Aprendices ────────────────────────────────────────────────────────────
    print("  → aprendiz...")
    apr_fixed = [APR1, APR2, APR3, APR4, APR5, APR6]
    for fixed_id, usr_id in zip(apr_fixed, usr_apr):
        cur.execute(
            "INSERT INTO aprendiz (id, persona_id, regional_id)"
            " VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
            (fixed_id, usr_id, regional_id),
        )
    apr = [_resolve_id(cur, "aprendiz", "persona_id", u) for u in usr_apr]

    # ── Perfil de acceso ──────────────────────────────────────────────────────
    print("  → usuario_perfil (Aprendiz)...")
    cur.execute(
        """
        INSERT INTO usuario_perfil (id, usuario_id, perfil_id)
        SELECT gen_random_uuid(), u, p.id
        FROM   (VALUES
                    (%s::uuid), (%s::uuid), (%s::uuid),
                    (%s::uuid), (%s::uuid), (%s::uuid)
               ) AS t(u)
        JOIN   perfil p ON p.nombre = 'Aprendiz'
        ON CONFLICT (usuario_id, perfil_id) DO NOTHING
        """,
        tuple(usr_apr),
    )

    # ── Empresas ──────────────────────────────────────────────────────────────
    print("  → empresa...")
    for emp_id, razon, nit, sector, correo, tel in [
        (EMP1, "TechSoft SAS",    "9005123456", "Tecnología",      "contacto@techsoft.com.co", "6075551234"),
        (EMP2, "Innovatech Ltda", "8002345678", "Consultoría TIC", "info@innovatech.com.co",   "6075559876"),
    ]:
        cur.execute(
            "INSERT INTO empresa (id, razon_social, nit, sector, correo, telefono)"
            " VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            (emp_id, razon, nit, sector, correo, tel),
        )
    emp1 = _resolve_id(cur, "empresa", "nit", "9005123456")
    emp2 = _resolve_id(cur, "empresa", "nit", "8002345678")

    # ── Inscripciones ficha_aprendiz ──────────────────────────────────────────
    # Solo estado formativo. La vinculación empresa ↔ aprendiz vive en
    # contrato_aprendizaje (seeds_etapa_productiva/01_contratos.py).
    print("  → ficha_aprendiz...")
    inscripciones = [
        # (fa_id, ficha_id, apr_id, en_lectiva, lectiva_concluida, en_ep)
        (FA1, ficha1, apr[0], True,  False, False),
        (FA2, ficha1, apr[1], False, True,  True),
        (FA3, ficha2, apr[2], True,  False, False),
        (FA4, ficha2, apr[3], False, True,  True),
        (FA5, ficha3, apr[4], True,  False, False),
        (FA6, ficha3, apr[5], False, True,  False),
    ]
    for row in inscripciones:
        cur.execute(
            """
            INSERT INTO ficha_aprendiz (
                id, ficha_id, aprendiz_id,
                en_etapa_lectiva, etapa_lectiva_concluida,
                en_etapa_productiva
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            row,
        )


if __name__ == "__main__":
    print("[ Seed 03 ] Aprendices, inscripciones y empresas EP")
    print(f"            Contraseña de todos: {PASSWORD}")
    with connect() as conn:
        with conn.cursor() as cur:
            run(cur)
        conn.commit()
    print("[ Seed 03 ] Listo.\n")
