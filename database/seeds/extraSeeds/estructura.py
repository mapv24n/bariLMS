import os
import uuid
import psycopg
from data import DATA_TIPO_DOCUMENTO, generate_id
from queries import SeedQueries  # Assuming your Enum is in queries.py

def connect():
    return psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE", "bari_lms"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", ""),
    )

def run(cur):
    print("  → Inserting tipo_documento using Query Registry...")
    
    for codigo, nombre in DATA_TIPO_DOCUMENTO:
        new_id = generate_id()
        
        # Using the Smart Enum method we implemented
        # It handles cur.execute(self.value, params) internally
        was_inserted = SeedQueries.INSERT_TIPO_DOC.execute(cur, (new_id, codigo, nombre))
        
        status = "[+]" if was_inserted else "[skipped]"
        print(f"    {status} Processed: {codigo}")

if __name__ == "__main__":
    print("[ Seed Test ] Starting refactored catalog seed...")
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                run(cur)
            conn.commit()
        print("[ Seed Test ] Success.")
    except Exception as e:
        print(f"[ Seed Test ] Failed: {e}")