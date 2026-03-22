"""
Ejecuta todos los seeds en orden desde la raíz del proyecto:
    python database/seeds/run_all.py
"""

import importlib.util
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "internal"))

import psycopg  # noqa: E402

SEEDS_DIR = os.path.dirname(__file__)
SEED_FILES = ["01_estructura.py", "02_instructores.py", "03_aprendices.py"]


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
    print("╔═══════════════════════════════════════╗")
    print("║   bariLMS — Carga completa de seeds   ║")
    print("╚═══════════════════════════════════════╝\n")

    with connect() as conn:
        with conn.cursor() as cur:
            for filename in SEED_FILES:
                label = filename.replace(".py", "")
                print(f"[ {label} ]")
                mod = load_seed(filename)
                mod.run(cur)
                print(f"[ {label} ] ✓\n")
        conn.commit()

    print("Todos los seeds aplicados correctamente.")
