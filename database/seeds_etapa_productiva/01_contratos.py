"""
Seed EP-01 — Contratos de aprendizaje.

Depende de: database/seeds/03_aprendices.py (debe ejecutarse primero).

Crea los registros de contrato_aprendizaje que vinculan aprendices
(a través de su ficha_aprendiz) con empresas.

Estado de los contratos creados:
    FA2 (luis.torres  / ficha 2900001) → TechSoft SAS    → activo
    FA4 (andres.ruiz  / ficha 2900002) → Innovatech Ltda → activo
    FA6 (miguel.castro / ficha 2900003) → sin contrato    (habilitado, pendiente)

Ejecutar desde la raíz del proyecto:
    python database/seeds_etapa_productiva/01_contratos.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "internal"))

import psycopg  # noqa: E402

# Fixed UUIDs para idempotencia
CT1 = "c5000000-0000-0000-0000-000000000001"
CT2 = "c5000000-0000-0000-0000-000000000002"

# NITs de las empresas creadas en seed 03
NIT_TECHSOFT    = "9005123456"
NIT_INNOVATECH  = "8002345678"

# Fichas de formación (número)
FICHA1_NUM = "2900001"
FICHA2_NUM = "2900002"

# Correos de los aprendices en EP
CORREO_APR2 = "luis.torres@aprendiz.sena.edu.co"
CORREO_APR4 = "andres.ruiz@aprendiz.sena.edu.co"


def connect():
    return psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE", "bari_lms"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", ""),
    )


def _one(cur, sql, params=()):
    cur.execute(sql, params)
    row = cur.fetchone()
    return str(row[0]) if row else None


def run(cur):
    # ── Resolver IDs desde datos existentes ───────────────────────────────────
    emp1 = _one(cur, "SELECT id FROM empresa WHERE nit = %s", (NIT_TECHSOFT,))
    emp2 = _one(cur, "SELECT id FROM empresa WHERE nit = %s", (NIT_INNOVATECH,))

    ficha1 = _one(cur, "SELECT id FROM ficha_formacion WHERE numero = %s", (FICHA1_NUM,))
    ficha2 = _one(cur, "SELECT id FROM ficha_formacion WHERE numero = %s", (FICHA2_NUM,))

    # ficha_aprendiz del aprendiz 2 en ficha 1
    fa2 = _one(
        cur,
        """
        SELECT fa.id FROM ficha_aprendiz fa
        JOIN aprendiz a   ON a.id   = fa.aprendiz_id
        JOIN persona  per ON per.id = a.persona_id
        JOIN usuario  u   ON u.id   = per.id
        WHERE u.correo = %s AND fa.ficha_id = %s
        """,
        (CORREO_APR2, ficha1),
    )

    # ficha_aprendiz del aprendiz 4 en ficha 2
    fa4 = _one(
        cur,
        """
        SELECT fa.id FROM ficha_aprendiz fa
        JOIN aprendiz a   ON a.id   = fa.aprendiz_id
        JOIN persona  per ON per.id = a.persona_id
        JOIN usuario  u   ON u.id   = per.id
        WHERE u.correo = %s AND fa.ficha_id = %s
        """,
        (CORREO_APR4, ficha2),
    )

    if not all([emp1, emp2, fa2, fa4]):
        raise RuntimeError(
            "Seed EP-01: no se encontraron todos los registros base. "
            "Ejecuta primero database/seeds/run_all.py."
        )

    # ── Contratos de aprendizaje ───────────────────────────────────────────────
    print("  → contrato_aprendizaje...")
    contratos = [
        # (id, ficha_aprendiz_id, empresa_id, fecha_inicio, fecha_fin, estado)
        (CT1, fa2, emp1, "2025-01-15", "2025-07-15", "activo"),
        (CT2, fa4, emp2, "2025-02-01", "2025-08-01", "activo"),
    ]
    for ct_id, fa_id, emp_id, inicio, fin, estado in contratos:
        cur.execute(
            """
            INSERT INTO contrato_aprendizaje
                (id, ficha_aprendiz_id, empresa_id, fecha_inicio, fecha_fin, estado)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (ct_id, fa_id, emp_id, inicio, fin, estado),
        )


if __name__ == "__main__":
    print("[ Seed EP-01 ] Contratos de aprendizaje")
    with connect() as conn:
        with conn.cursor() as cur:
            run(cur)
        conn.commit()
    print("[ Seed EP-01 ] Listo.\n")
