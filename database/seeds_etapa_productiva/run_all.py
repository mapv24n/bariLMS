"""
Ejecuta los seeds específicos del módulo Etapa Productiva en orden.

Requiere que los seeds base ya estén aplicados:
    python database/seeds/run_all.py

Luego, desde la raíz del proyecto:
    python database/seeds_etapa_productiva/run_all.py
"""

import importlib.util
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "internal"))

import psycopg  # noqa: E402

SEEDS_DIR  = os.path.dirname(__file__)
SEED_FILES = ["01_contratos.py"]


def load_seed(filename):
    path = os.path.join(SEEDS_DIR, filename)
    spec = importlib.util.spec_from_file_location(filename, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def connect():
    return psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE", "bari_lms"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", ""),
    )


if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════╗")
    print("║   bariLMS — Seeds módulo Etapa Productiva        ║")
    print("╚══════════════════════════════════════════════════╝\n")

    with connect() as conn:
        with conn.cursor() as cur:
            for filename in SEED_FILES:
                label = filename.replace(".py", "")
                print(f"[ {label} ]")
                mod = load_seed(filename)
                mod.run(cur)
                print(f"[ {label} ] ✓\n")
        conn.commit()

    print("Seeds de Etapa Productiva aplicados correctamente.")
