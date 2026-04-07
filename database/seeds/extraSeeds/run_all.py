"""
run_all.py — Master runner. Executes all extraSeeds in dependency order.

Run from project root:
    python database/seeds/extraSeeds/run_all.py
"""

import importlib.util
import os
import sys

SEEDS_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, SEEDS_DIR)
sys.path.insert(0, os.path.join(SEEDS_DIR, "..", "..", "..", "internal"))

from db import connect  # noqa: E402

SEED_FILES = [
    "estructura.py",
    "instructores.py",
    "aprendices.py",
    "actividades.py",
]


def load_seed(filename):
    path = os.path.join(SEEDS_DIR, filename)
    spec = importlib.util.spec_from_file_location(filename, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


if __name__ == "__main__":
    print("╔══════════════════════════════════════════╗")
    print("║    bariLMS — Carga completa de seeds     ║")
    print("╚══════════════════════════════════════════╝\n")

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
    print("\n── Ficha IDs (usa estos en las URLs) ──────────────────────────────")
    with connect() as conn:
        with conn.cursor() as cur:
            rows = cur.execute(
                "SELECT numero, id FROM ficha_formacion ORDER BY numero"
            ).fetchall()
            for numero, fid in rows:
                print(f"  Ficha {numero}  →  /instructor/ficha/{fid}/fases")
