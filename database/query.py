"""
database/query.py - Interactive SQL query runner for bariLMS.

Connects to the PostgreSQL database using the same PG* environment variables
as the rest of the project and prints query results in a readable ASCII table.

Usage:
    # Single query from command line argument
    python database/query.py "SELECT * FROM ficha_aprendiz LIMIT 5"

    # Interactive mode (prompts for input)
    python database/query.py

    # Multi-line query in interactive mode: end with a blank line or semicolon
"""

import os
import sys

# Load .env from project root
from pathlib import Path
_root = Path(__file__).resolve().parent.parent
_env  = _root / ".env"
if _env.exists():
    from dotenv import load_dotenv
    load_dotenv(_env)

import psycopg
import psycopg.rows


# ── Connection ────────────────────────────────────────────────────────────────

def connect():
    return psycopg.connect(
        host=os.getenv("PGHOST",     "127.0.0.1"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE", "bari_lms"),
        user=os.getenv("PGUSER",     "postgres"),
        password=os.getenv("PGPASSWORD", ""),
        options="-c client_encoding=UTF8",
        row_factory=psycopg.rows.dict_row,
    )


# ── Formatting ────────────────────────────────────────────────────────────────

def _cell(value):
    """Normalize a cell value to a printable string."""
    if value is None:
        return "NULL"
    return str(value)


def print_table(rows: list[dict]):
    if not rows:
        print("(0 rows)")
        return

    headers = list(rows[0].keys())
    columns = {h: len(h) for h in headers}

    # Measure widths
    for row in rows:
        for h in headers:
            columns[h] = max(columns[h], len(_cell(row[h])))

    # Header
    sep  = "+" + "+".join("-" * (w + 2) for w in columns.values()) + "+"
    head = "|" + "|".join(f" {h:<{columns[h]}} " for h in headers) + "|"
    print(sep)
    print(head)
    print(sep)

    # Rows
    for row in rows:
        line = "|" + "|".join(f" {_cell(row[h]):<{columns[h]}} " for h in headers) + "|"
        print(line)

    print(sep)
    print(f"({len(rows)} row{'s' if len(rows) != 1 else ''})")


# ── Execution ─────────────────────────────────────────────────────────────────

def run_query(conn, sql: str):
    sql = sql.strip().rstrip(";")
    if not sql:
        return

    with conn.cursor() as cur:
        try:
            cur.execute(sql)

            # DML / DDL — no result set
            if cur.description is None:
                conn.commit()
                print(f"OK  ({cur.rowcount} row{'s' if cur.rowcount != 1 else ''} affected)")
                return

            rows = cur.fetchall()
            print_table(rows)

        except psycopg.Error as e:
            conn.rollback()
            print(f"ERROR: {e}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    try:
        conn = connect()
    except psycopg.OperationalError as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

    # Single query passed as CLI argument
    if len(sys.argv) > 1:
        sql = " ".join(sys.argv[1:])
        run_query(conn, sql)
        conn.close()
        return

    # Interactive mode
    print("bariLMS query runner  |  type SQL and press Enter twice (or end with ;)")
    print("Type 'exit' or Ctrl+C to quit.\n")

    try:
        while True:
            lines = []
            try:
                first = input("sql> ").strip()
            except EOFError:
                break

            if first.lower() in ("exit", "quit", r"\q"):
                break

            # Collect lines until blank line or trailing semicolon
            lines.append(first)
            if not first.endswith(";"):
                try:
                    while True:
                        line = input("  -> ").strip()
                        if line == "":
                            break
                        lines.append(line)
                        if line.endswith(";"):
                            break
                except EOFError:
                    pass

            sql = " ".join(lines)
            if sql:
                run_query(conn, sql)
            print()

    except KeyboardInterrupt:
        print("\nBye.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
