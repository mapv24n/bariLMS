"""Gestión del pool de conexiones y acceso a la base de datos PostgreSQL."""

import psycopg
import psycopg.conninfo
from flask import current_app, g
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


class CursorWrapper:
    def __init__(self, cursor=None):
        self.cursor = cursor

    def fetchone(self):
        if self.cursor is None:
            return None
        try:
            return self.cursor.fetchone()
        finally:
            self.cursor.close()
            self.cursor = None

    def fetchall(self):
        if self.cursor is None:
            return []
        try:
            return self.cursor.fetchall()
        finally:
            self.cursor.close()
            self.cursor = None


class PostgresConnection:
    def __init__(self, connection):
        self.connection = connection

    @staticmethod
    def _normalize_query(query):
        return query.replace("?", "%s")

    def execute(self, query, params=()):
        cursor = self.connection.cursor(row_factory=dict_row)
        cursor.execute(self._normalize_query(query), params)
        if cursor.description is None:
            cursor.close()
            return CursorWrapper()
        return CursorWrapper(cursor)

    def executemany(self, query, seq_of_params):
        cursor = self.connection.cursor()
        try:
            cursor.executemany(self._normalize_query(query), seq_of_params)
        finally:
            cursor.close()
        return CursorWrapper()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()


def parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_uuid(value):
    """Retorna un UUID como string limpio, o None si está vacío."""
    if value is None:
        return None
    stripped = str(value).strip()
    return stripped if stripped else None


def create_pool(app):
    conninfo = psycopg.conninfo.make_conninfo(
        host=app.config["PGHOST"],
        port=app.config["PGPORT"],
        dbname=app.config["PGDATABASE"],
        user=app.config["PGUSER"],
        password=app.config["PGPASSWORD"],
        options="-c TimeZone=America/Bogota",
    )
    return ConnectionPool(conninfo, min_size=2, max_size=10, open=True)


def get_db():
    if "db" not in g:
        conn = current_app.extensions["db_pool"].getconn()
        g._pool_conn = conn
        g.db = PostgresConnection(conn)
    return g.db


def close_db(_error=None):
    conn = g.pop("_pool_conn", None)
    g.pop("db", None)
    if conn is not None:
        current_app.extensions["db_pool"].putconn(conn)
