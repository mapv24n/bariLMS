"""
db.py — Shared database utilities for all extraSeeds scripts.

Import this instead of duplicating connect() / resolve_id() in every seed file.
"""

import os
import psycopg


def connect():
    return psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE", "bari_lms"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", ""),
    )


def resolve_id(cur, table, col, val):
    """Returns the UUID string of the row found by natural key, or None."""
    cur.execute(f"SELECT id FROM {table} WHERE {col} = %s", (val,))
    row = cur.fetchone()
    return str(row[0]) if row else None
