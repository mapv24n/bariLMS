import copy

import psycopg
import psycopg.conninfo
from flask import current_app, g
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from bari_lms.config import DASHBOARDS, DEFAULT_LEVELS, DEFAULT_USERS
from bari_lms.services.security import hash_password

ENTITY_CONFIG = {
    "regional": {
        "table": "regional",
        "label": "Regional",
        "parent_key": None,
        "fields": ["nombre"],
        "required": ["nombre"],
        "context_key": "regional_id",
        "select_aliases": {},
        "form_to_db": {},
    },
    "centro": {
        "table": "centro",
        "label": "Centro de formación",
        "parent_key": "regional_id",
        "fields": ["regional_id", "nombre"],
        "required": ["regional_id", "nombre"],
        "context_key": "centro_id",
        "select_aliases": {},
        "form_to_db": {},
    },
    "coordinacion": {
        "table": "coordinacion",
        "label": "Coordinación",
        "parent_key": "centro_id",
        "fields": ["centro_id", "nombre"],
        "required": ["centro_id", "nombre"],
        "context_key": "coordinacion_id",
        "select_aliases": {},
        "form_to_db": {},
    },
    "sede": {
        "table": "sede",
        "label": "Sede",
        "parent_key": "centro_id",
        "fields": ["centro_id", "nombre"],
        "required": ["centro_id", "nombre"],
        "context_key": "sede_id",
        "select_aliases": {},
        "form_to_db": {},
    },
    "instructor": {
        "table": "instructor",
        "label": "Instructor",
        "parent_key": "centro_id",
        "fields": ["centro_id", "area_id", "documento", "nombres", "apellidos", "correo"],
        "required": ["centro_id", "documento", "nombres", "apellidos"],
        "context_key": "centro_id",
        "select_aliases": {
            "correo": "email",
            "usuario_id": "user_id",
        },
        "form_to_db": {"email": "correo"},
    },
    "aprendiz": {
        "table": "aprendiz",
        "label": "Aprendiz",
        "parent_key": "regional_id",
        "fields": ["regional_id", "documento", "nombres", "apellidos", "correo", "ficha"],
        "required": ["regional_id", "documento", "nombres", "apellidos"],
        "context_key": "regional_id",
        "select_aliases": {"correo": "email", "usuario_id": "user_id"},
        "form_to_db": {},
    },
    "ambiente": {
        "table": "ambiente",
        "label": "Ambiente",
        "parent_key": "sede_id",
        "fields": ["sede_id", "nombre", "capacidad"],
        "required": ["sede_id", "nombre"],
        "context_key": "sede_id",
        "select_aliases": {},
        "form_to_db": {},
    },
    "red": {
        "table": "red_conocimiento",
        "label": "Red de conocimiento",
        "parent_key": None,
        "fields": ["nombre"],
        "required": ["nombre"],
        "context_key": "red_id",
        "select_aliases": {},
        "form_to_db": {},
    },
    "area": {
        "table": "area",
        "label": "Area",
        "parent_key": "red_id",
        "fields": ["red_conocimiento_id", "nombre"],
        "required": ["red_conocimiento_id", "nombre"],
        "context_key": "area_id",
        "select_aliases": {"red_conocimiento_id": "red_id"},
        "form_to_db": {"red_id": "red_conocimiento_id"},
    },
    "nivel": {
        "table": "nivel_formacion",
        "label": "Nivel de formación",
        "parent_key": None,
        "fields": ["nombre"],
        "required": ["nombre"],
        "context_key": "nivel_id",
        "select_aliases": {},
        "form_to_db": {},
    },
    "programa": {
        "table": "programa_formacion",
        "label": "Programa de formación",
        "parent_key": "area_id",
        "fields": ["area_id", "nivel_formacion_id", "nombre"],
        "required": ["area_id", "nivel_formacion_id", "nombre"],
        "context_key": "programa_id",
        "select_aliases": {"nivel_formacion_id": "nivel_id"},
        "form_to_db": {"nivel_id": "nivel_formacion_id"},
    },
    "ficha": {
        "table": "ficha_formacion",
        "label": "Ficha de formación",
        "parent_key": "programa_id",
        "fields": ["numero", "programa_formacion_id", "proyecto_formativo_id", "coordinacion_id", "instructor_id"],
        "required": ["numero", "programa_formacion_id", "proyecto_formativo_id", "coordinacion_id"],
        "context_key": "programa_id",
        "select_aliases": {
            "programa_formacion_id": "programa_id",
        },
        "form_to_db": {
            "programa_id": "programa_formacion_id",
        },
    },
    "proyecto_formativo": {
        "table": "proyecto_formativo",
        "label": "Proyecto formativo",
        "parent_key": None,
        "fields": ["codigo", "nombre"],
        "required": ["codigo", "nombre"],
        "context_key": "proyecto_formativo_id",
        "select_aliases": {},
        "form_to_db": {},
    },
    "fase_proyecto": {
        "table": "fase_proyecto",
        "label": "Fase del proyecto",
        "parent_key": "proyecto_formativo_id",
        "fields": ["proyecto_formativo_id", "nombre"],
        "required": ["proyecto_formativo_id", "nombre"],
        "context_key": "fase_id",
        "select_aliases": {},
        "form_to_db": {},
    },
    "actividad_proyecto": {
        "table": "actividad_proyecto",
        "label": "Actividad del proyecto",
        "parent_key": "fase_id",
        "fields": ["fase_proyecto_id", "nombre"],
        "required": ["fase_proyecto_id", "nombre"],
        "context_key": "fase_id",
        "select_aliases": {"fase_proyecto_id": "fase_id"},
        "form_to_db": {"fase_id": "fase_proyecto_id"},
    },
    "actividad_aprendizaje": {
        "table": "actividad_aprendizaje",
        "label": "Actividad de aprendizaje",
        "parent_key": "actividad_proyecto_id",
        "fields": ["actividad_proyecto_id", "nombre"],
        "required": ["actividad_proyecto_id", "nombre"],
        "context_key": "actividad_proyecto_id",
        "select_aliases": {},
        "form_to_db": {},
    },
    "administrativo_persona": {
        "table": "personal_administrativo",
        "label": "Personal administrativo",
        "parent_key": "centro_id",
        "fields": ["centro_id", "documento", "nombres", "apellidos", "correo", "cargo"],
        "required": ["centro_id", "documento", "nombres", "apellidos", "cargo"],
        "context_key": "centro_id",
        "select_aliases": {"correo": "email", "usuario_id": "user_id"},
        "form_to_db": {},
    },
}

LEGACY_TABLE_NAMES = {
    "users": "usuario",
    "regionales": "regional",
    "centros": "centro",
    "coordinaciones": "coordinacion",
    "sedes": "sede",
    "instructores": "instructor",
    "aprendices": "aprendiz",
    "ambientes": "ambiente",
}

STRUCTURE_ENTITIES = {"regional", "centro", "coordinacion", "sede", "ambiente"}
PEOPLE_ENTITIES = {"instructor", "aprendiz", "administrativo_persona"}
ACADEMIC_ENTITIES = {"red", "area", "nivel", "programa", "ficha", "proyecto_formativo", "fase_proyecto", "actividad_proyecto", "actividad_aprendizaje"}

COLUMN_RENAMES = {
    "usuario": {
        "email": "correo",
        "password_hash": "contrasena_hash",
        "role": "rol",
        "name": "nombre",
        "active": "activo",
        "created_at": "creado_en",
    },
    # Legacy id_xxx → xxx_id renames (applied by initialize_database on old schemas)
    "centro": {"id_regional": "regional_id"},
    "coordinacion": {"id_centro": "centro_id"},
    "sede": {"id_centro": "centro_id"},
    "instructor": {
        "id_coordinacion": "centro_id",
        "id_centro": "centro_id",
        "id_area": "area_id",
        "id_usuario": "usuario_id",
    },
    "aprendiz": {
        "id_coordinacion": "regional_id",
        "id_regional": "regional_id",
        "id_usuario": "usuario_id",
    },
    "ambiente": {"id_sede": "sede_id"},
    "programa_formacion": {
        "id_area": "area_id",
        "id_nivel_formacion": "nivel_formacion_id",
    },
    "ficha_formacion": {
        "id_programa_formacion": "programa_formacion_id",
        "id_proyecto_formativo": "proyecto_formativo_id",
        "id_coordinacion": "coordinacion_id",
        "id_instructor": "instructor_id",
    },
    "fase_proyecto": {"id_proyecto_formativo": "proyecto_formativo_id"},
    "actividad_proyecto": {"id_fase_proyecto": "fase_proyecto_id"},
    "actividad_aprendizaje": {"id_actividad_proyecto": "actividad_proyecto_id"},
    "personal_administrativo": {"id_centro": "centro_id", "id_usuario": "usuario_id"},
    "area": {"id_red_conocimiento": "red_conocimiento_id"},
    "guia_aprendizaje": {"id_actividad_aprendizaje": "actividad_aprendizaje_id"},
    "evidencia_aprendizaje": {"id_actividad_aprendizaje": "actividad_aprendizaje_id"},
    "entrega_evidencia": {"id_evidencia_aprendizaje": "evidencia_aprendizaje_id", "id_usuario": "usuario_id"},
    "seccion_actividad": {"id_actividad_aprendizaje": "actividad_aprendizaje_id"},
    "sub_seccion_actividad": {"id_seccion": "seccion_id"},
    "guia_actividad_proyecto": {"id_actividad_proyecto": "actividad_proyecto_id"},
    "ficha_instructor_competencia": {"id_ficha": "ficha_id", "id_instructor": "instructor_id"},
    "asistencia_aprendiz": {"id_ficha": "ficha_id", "id_aprendiz": "aprendiz_id"},
}

PERSON_USER_CONFIG = {
    "instructor": {
        "role": "Instructor",
        "email_prefix": "instructor",
        "table": "instructor",
        "email_column": "correo",
        "user_column": "usuario_id",
    },
    "aprendiz": {
        "role": "Aprendiz",
        "email_prefix": "aprendiz",
        "table": "aprendiz",
        "email_column": "correo",
        "user_column": "usuario_id",
    },
    "administrativo_persona": {
        "role": "Administrativo",
        "email_prefix": "administrativo",
        "table": "personal_administrativo",
        "email_column": "correo",
        "user_column": "usuario_id",
    },
}


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
    """Return a stripped UUID string, or None if blank/None."""
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


def get_existing_tables():
    return {
        row["name"]
        for row in get_db().execute(
            """
            SELECT tablename AS name
            FROM pg_tables
            WHERE schemaname = 'public'
            """
        ).fetchall()
    }


def get_table_columns(table_name):
    return {
        row["name"]
        for row in get_db().execute(
            """
            SELECT column_name AS name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = ?
            """,
            (table_name,),
        ).fetchall()
    }


def constraint_exists(table_name, constraint_name):
    row = get_db().execute(
        """
        SELECT 1 AS exists_flag
        FROM information_schema.table_constraints
        WHERE table_schema = 'public' AND table_name = ? AND constraint_name = ?
        """,
        (table_name, constraint_name),
    ).fetchone()
    return row is not None


def initialize_database():
    db = get_db()
    existing_tables = get_existing_tables()
    for old_name, new_name in LEGACY_TABLE_NAMES.items():
        if old_name in existing_tables and new_name not in existing_tables:
            db.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")
            existing_tables.remove(old_name)
            existing_tables.add(new_name)

    for table_name, rename_map in COLUMN_RENAMES.items():
        if table_name not in existing_tables:
            continue
        table_columns = get_table_columns(table_name)
        for old_column, new_column in rename_map.items():
            if old_column in table_columns and new_column not in table_columns:
                db.execute(f"ALTER TABLE {table_name} RENAME COLUMN {old_column} TO {new_column}")
                table_columns.remove(old_column)
                table_columns.add(new_column)

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS usuario (
            id              UUID        PRIMARY KEY,
            creado_por      UUID        REFERENCES usuario(id) ON DELETE SET NULL,
            correo          TEXT        UNIQUE NOT NULL,
            contrasena_hash TEXT        NOT NULL,
            nombre          TEXT        NOT NULL,
            activo          BOOLEAN     NOT NULL DEFAULT TRUE,
            creado_en       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en  TIMESTAMPTZ
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS perfil (
            id             UUID        PRIMARY KEY,
            nombre         TEXT        NOT NULL UNIQUE,
            descripcion    TEXT,
            creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ,
            creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS rol (
            id             UUID        PRIMARY KEY,
            perfil_id      UUID        NOT NULL REFERENCES perfil(id) ON DELETE CASCADE,
            nombre         TEXT        NOT NULL,
            descripcion    TEXT,
            creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ,
            creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,
            UNIQUE (perfil_id, nombre)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS permiso (
            id             UUID        PRIMARY KEY,
            codigo         TEXT        NOT NULL UNIQUE,
            nombre         TEXT        NOT NULL,
            descripcion    TEXT,
            creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ,
            creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS rol_permiso (
            id             UUID        PRIMARY KEY,
            rol_id         UUID        NOT NULL REFERENCES rol(id) ON DELETE CASCADE,
            permiso_id     UUID        NOT NULL REFERENCES permiso(id) ON DELETE CASCADE,
            creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ,
            creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,
            UNIQUE (rol_id, permiso_id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS usuario_perfil (
            id             UUID        PRIMARY KEY,
            usuario_id     UUID        NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
            perfil_id      UUID        NOT NULL REFERENCES perfil(id) ON DELETE CASCADE,
            creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ,
            creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,
            UNIQUE (usuario_id, perfil_id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS usuario_rol (
            id             UUID        PRIMARY KEY,
            usuario_id     UUID        NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
            rol_id         UUID        NOT NULL REFERENCES rol(id) ON DELETE CASCADE,
            creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ,
            creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,
            UNIQUE (usuario_id, rol_id)
        )
        """
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS regional ("
        "id UUID PRIMARY KEY, "
        "nombre TEXT NOT NULL UNIQUE, "
        "creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(), "
        "actualizado_en TIMESTAMPTZ)"
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS centro (
            id             UUID        PRIMARY KEY,
            regional_id    UUID        NOT NULL REFERENCES regional(id) ON DELETE RESTRICT,
            nombre         TEXT        NOT NULL,
            creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS coordinacion (
            id             UUID        PRIMARY KEY,
            centro_id      UUID        NOT NULL REFERENCES centro(id) ON DELETE RESTRICT,
            nombre         TEXT        NOT NULL,
            creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS sede (
            id             UUID        PRIMARY KEY,
            centro_id      UUID        NOT NULL REFERENCES centro(id) ON DELETE RESTRICT,
            nombre         TEXT        NOT NULL,
            creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS instructor (
            id             UUID        PRIMARY KEY,
            centro_id      UUID        NOT NULL REFERENCES centro(id) ON DELETE RESTRICT,
            area_id        UUID        REFERENCES area(id) ON DELETE SET NULL,
            usuario_id     UUID        REFERENCES usuario(id) ON DELETE SET NULL,
            documento      TEXT        NOT NULL,
            nombres        TEXT        NOT NULL,
            apellidos      TEXT        NOT NULL,
            correo         TEXT,
            genero         TEXT        NOT NULL DEFAULT 'M',
            creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS aprendiz (
            id             UUID        PRIMARY KEY,
            regional_id    UUID        NOT NULL REFERENCES regional(id) ON DELETE RESTRICT,
            usuario_id     UUID        REFERENCES usuario(id) ON DELETE SET NULL,
            documento      TEXT        NOT NULL,
            nombres        TEXT        NOT NULL,
            apellidos      TEXT        NOT NULL,
            correo         TEXT,
            ficha          TEXT,
            creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS personal_administrativo (
            id             UUID        PRIMARY KEY,
            centro_id      UUID        NOT NULL REFERENCES centro(id) ON DELETE RESTRICT,
            usuario_id     UUID        REFERENCES usuario(id) ON DELETE SET NULL,
            documento      TEXT        NOT NULL,
            nombres        TEXT        NOT NULL,
            apellidos      TEXT        NOT NULL,
            correo         TEXT,
            cargo          TEXT        NOT NULL,
            creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS ambiente (
            id             UUID        PRIMARY KEY,
            sede_id        UUID        NOT NULL REFERENCES sede(id) ON DELETE RESTRICT,
            nombre         TEXT        NOT NULL,
            capacidad      INTEGER,
            creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ
        )
        """
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS red_conocimiento ("
        "id UUID PRIMARY KEY, "
        "nombre TEXT NOT NULL UNIQUE, "
        "creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(), "
        "actualizado_en TIMESTAMPTZ)"
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS area (
            id                  UUID        PRIMARY KEY,
            red_conocimiento_id UUID        NOT NULL REFERENCES red_conocimiento(id) ON DELETE RESTRICT,
            nombre              TEXT        NOT NULL,
            creado_en           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS nivel_formacion ("
        "id UUID PRIMARY KEY, "
        "nombre TEXT NOT NULL UNIQUE, "
        "creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(), "
        "actualizado_en TIMESTAMPTZ)"
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS programa_formacion (
            id                 UUID        PRIMARY KEY,
            area_id            UUID        NOT NULL REFERENCES area(id) ON DELETE RESTRICT,
            nivel_formacion_id UUID        NOT NULL REFERENCES nivel_formacion(id) ON DELETE RESTRICT,
            nombre             TEXT        NOT NULL,
            creado_en          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en     TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS proyecto_formativo (
            id             UUID        PRIMARY KEY,
            codigo         TEXT        NOT NULL UNIQUE,
            nombre         TEXT        NOT NULL,
            creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS ficha_formacion (
            id                    UUID        PRIMARY KEY,
            numero                TEXT        NOT NULL UNIQUE,
            programa_formacion_id UUID        NOT NULL REFERENCES programa_formacion(id) ON DELETE RESTRICT,
            proyecto_formativo_id UUID        REFERENCES proyecto_formativo(id) ON DELETE SET NULL,
            coordinacion_id       UUID        NOT NULL REFERENCES coordinacion(id) ON DELETE RESTRICT,
            instructor_id         UUID        REFERENCES instructor(id) ON DELETE SET NULL,
            creado_en             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en        TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS fase_proyecto (
            id                    UUID        PRIMARY KEY,
            proyecto_formativo_id UUID        NOT NULL REFERENCES proyecto_formativo(id) ON DELETE CASCADE,
            nombre                TEXT        NOT NULL,
            creado_en             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en        TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS actividad_proyecto (
            id               UUID        PRIMARY KEY,
            fase_proyecto_id UUID        NOT NULL REFERENCES fase_proyecto(id) ON DELETE CASCADE,
            nombre           TEXT        NOT NULL,
            creado_en        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en   TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS actividad_aprendizaje (
            id                    UUID        PRIMARY KEY,
            actividad_proyecto_id UUID        NOT NULL REFERENCES actividad_proyecto(id) ON DELETE CASCADE,
            nombre                TEXT        NOT NULL,
            descripcion           TEXT,
            fecha_inicio          DATE,
            fecha_fin             DATE,
            orden                 INTEGER     NOT NULL DEFAULT 0,
            creado_en             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en        TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS guia_aprendizaje (
            id                       UUID        PRIMARY KEY,
            actividad_aprendizaje_id UUID        NOT NULL UNIQUE REFERENCES actividad_aprendizaje(id) ON DELETE CASCADE,
            url                      TEXT        NOT NULL,
            subido_en                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            creado_en                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en           TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS evidencia_aprendizaje (
            id                       UUID        PRIMARY KEY,
            actividad_aprendizaje_id UUID        NOT NULL UNIQUE REFERENCES actividad_aprendizaje(id) ON DELETE CASCADE,
            descripcion              TEXT,
            creado_en                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en           TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS entrega_evidencia (
            id                       UUID        PRIMARY KEY,
            evidencia_aprendizaje_id UUID        NOT NULL REFERENCES evidencia_aprendizaje(id) ON DELETE CASCADE,
            usuario_id               UUID        NOT NULL REFERENCES usuario(id) ON DELETE RESTRICT,
            url                      TEXT,
            calificacion             NUMERIC(5,2),
            observaciones            TEXT,
            retroalimentacion        TEXT,
            aprueba                  BOOLEAN,
            calificado_en            TIMESTAMPTZ,
            entregado_en             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            creado_en                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (evidencia_aprendizaje_id, usuario_id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS seccion_actividad (
            id                       UUID        PRIMARY KEY,
            actividad_aprendizaje_id UUID        NOT NULL REFERENCES actividad_aprendizaje(id) ON DELETE CASCADE,
            nombre                   TEXT        NOT NULL,
            descripcion              TEXT,
            archivo_url              TEXT,
            archivo_tipo             TEXT,
            fecha_inicio             DATE,
            fecha_fin                DATE,
            orden                    INTEGER     NOT NULL DEFAULT 0,
            creado_en                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en           TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS sub_seccion_actividad (
            id             UUID        PRIMARY KEY,
            seccion_id     UUID        NOT NULL REFERENCES seccion_actividad(id) ON DELETE CASCADE,
            nombre         TEXT        NOT NULL,
            descripcion    TEXT,
            archivo_url    TEXT,
            archivo_tipo   TEXT,
            fecha_inicio   DATE,
            fecha_fin      DATE,
            orden          INTEGER     NOT NULL DEFAULT 0,
            creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS ficha_instructor_competencia (
            id             UUID        PRIMARY KEY,
            ficha_id       UUID        NOT NULL REFERENCES ficha_formacion(id) ON DELETE CASCADE,
            instructor_id  UUID        NOT NULL REFERENCES instructor(id) ON DELETE CASCADE,
            creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ,
            UNIQUE (ficha_id, instructor_id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS guia_actividad_proyecto (
            id                    UUID        PRIMARY KEY,
            actividad_proyecto_id UUID        NOT NULL REFERENCES actividad_proyecto(id) ON DELETE CASCADE,
            nombre                TEXT,
            descripcion           TEXT,
            url                   TEXT        NOT NULL,
            orden                 INTEGER     NOT NULL DEFAULT 0,
            subido_en             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            creado_en             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en        TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS asistencia_aprendiz (
            id             UUID        PRIMARY KEY,
            ficha_id       UUID        NOT NULL REFERENCES ficha_formacion(id) ON DELETE CASCADE,
            aprendiz_id    UUID        NOT NULL REFERENCES aprendiz(id) ON DELETE CASCADE,
            fecha          DATE        NOT NULL,
            estado         TEXT        NOT NULL DEFAULT 'Presente',
            creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ,
            UNIQUE (ficha_id, aprendiz_id, fecha)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS fase (
            id             UUID         PRIMARY KEY,
            nombre         VARCHAR(150) NOT NULL,
            orden          SMALLINT     NOT NULL DEFAULT 1,
            descripcion    TEXT,
            creado_en      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS notificacion (
            id             UUID        PRIMARY KEY,
            usuario_id     UUID        NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
            mensaje        TEXT        NOT NULL,
            tipo           VARCHAR(10) NOT NULL DEFAULT 'info'
                               CHECK (tipo IN ('info', 'success', 'warning', 'danger')),
            leida          BOOLEAN     NOT NULL DEFAULT FALSE,
            url_destino    TEXT,
            creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            actualizado_en TIMESTAMPTZ
        )
        """
    )
    db.commit()

    import uuid as _uuid

    db.execute(
        """
        INSERT INTO perfil (id, nombre) VALUES
            (gen_random_uuid(), 'Administrador'),
            (gen_random_uuid(), 'Administrativo'),
            (gen_random_uuid(), 'Instructor'),
            (gen_random_uuid(), 'Aprendiz')
        ON CONFLICT (nombre) DO NOTHING
        """
    )

    user_count = db.execute("SELECT COUNT(*) AS total FROM usuario").fetchone()["total"]
    if user_count == 0:
        for user in DEFAULT_USERS:
            user_id = str(_uuid.uuid4())
            db.execute(
                """
                INSERT INTO usuario (id, correo, contrasena_hash, nombre, activo)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, user["email"], hash_password(user["password"]), user["name"], user["active"]),
            )
            db.execute(
                """
                INSERT INTO usuario_perfil (id, usuario_id, perfil_id)
                SELECT %s, %s, p.id FROM perfil p WHERE p.nombre = %s
                ON CONFLICT (usuario_id, perfil_id) DO NOTHING
                """,
                (str(_uuid.uuid4()), user_id, user["role"]),
            )
        db.commit()

    level_count = db.execute("SELECT COUNT(*) AS total FROM nivel_formacion").fetchone()["total"]
    if level_count == 0:
        db.executemany(
            "INSERT INTO nivel_formacion (nombre) VALUES (?)",
            [(level,) for level in DEFAULT_LEVELS],
        )
        db.commit()


def get_user_by_email(email):
    if not email:
        return None
    return get_db().execute(
        """
        SELECT u.id, u.correo AS email, u.nombre AS name, u.activo AS active,
               u.creado_en AS created_at, u.contrasena_hash AS password_hash
        FROM usuario u
        WHERE lower(u.correo) = lower(%s)
        """,
        (email,),
    ).fetchone()


def user_has_profile(user_id, profile_name):
    row = get_db().execute(
        """
        SELECT 1
        FROM usuario_perfil up
        JOIN perfil p ON p.id = up.perfil_id
        WHERE up.usuario_id = %s AND p.nombre = %s
        """,
        (user_id, profile_name),
    ).fetchone()
    return row is not None


def get_user_by_id(user_id):
    return get_db().execute(
        """
        SELECT u.id, u.correo AS email, u.nombre AS name, u.activo AS active,
               u.creado_en AS created_at,
               (SELECT p.nombre FROM usuario_perfil up
                JOIN perfil p ON p.id = up.perfil_id
                WHERE up.usuario_id = u.id LIMIT 1) AS role
        FROM usuario u
        WHERE u.id = %s
        """,
        (user_id,),
    ).fetchone()


def get_all_users():
    return get_db().execute(
        """
        SELECT u.id, u.correo AS email, u.nombre AS name, u.activo AS active,
               u.creado_en AS created_at,
               (SELECT p.nombre FROM usuario_perfil up
                JOIN perfil p ON p.id = up.perfil_id
                WHERE up.usuario_id = u.id LIMIT 1) AS role
        FROM usuario u
        ORDER BY u.creado_en DESC, u.id DESC
        """
    ).fetchall()


def person_full_name(data):
    return f"{data['nombres']} {data['apellidos']}".strip()


def generate_person_email(prefix, documento, email):
    clean_email = (email or "").strip().lower()
    if clean_email:
        return clean_email
    return f"{prefix}.{documento}@barilms.local"


def create_linked_person_user(entity, item_id, data):
    config = PERSON_USER_CONFIG[entity]
    login_email = generate_person_email(config["email_prefix"], data["documento"], data.get("correo"))
    if get_user_by_email(login_email) is not None:
        raise ValueError("Ya existe un usuario con el correo que se intenta asignar a la persona.")

    import uuid as _uuid

    db = get_db()
    new_user_id = str(_uuid.uuid4())
    db.execute(
        """
        INSERT INTO usuario (id, correo, contrasena_hash, nombre, activo)
        VALUES (%s, %s, %s, %s, TRUE)
        """,
        (new_user_id, login_email, hash_password(data["documento"]), person_full_name(data)),
    )
    db.execute(
        """
        INSERT INTO usuario_perfil (id, usuario_id, perfil_id)
        SELECT %s, %s, p.id FROM perfil p WHERE p.nombre = %s
        ON CONFLICT (usuario_id, perfil_id) DO NOTHING
        """,
        (str(_uuid.uuid4()), new_user_id, config["role"]),
    )
    db.execute(
        f"""
        UPDATE {config['table']}
        SET {config['email_column']} = %s, {config['user_column']} = %s
        WHERE id = %s
        """,
        (login_email, new_user_id, item_id),
    )
    db.commit()
    return new_user_id


def sync_linked_person_user(entity, item_id, data):
    item = get_entity(entity, item_id)
    if item is None:
        return

    config = PERSON_USER_CONFIG[entity]
    login_email = generate_person_email(config["email_prefix"], data["documento"], data.get("correo"))
    db = get_db()

    if item["user_id"]:
        existing_user = get_user_by_email(login_email)
        if existing_user is not None and existing_user["id"] != item["user_id"]:
            raise ValueError("Ya existe un usuario con el correo que se intenta asignar a la persona.")

        import uuid as _uuid

        db.execute(
            """
            UPDATE usuario
            SET correo = %s, contrasena_hash = %s, nombre = %s, activo = TRUE
            WHERE id = %s
            """,
            (login_email, hash_password(data["documento"]), person_full_name(data), item["user_id"]),
        )
        db.execute(
            """
            INSERT INTO usuario_perfil (id, usuario_id, perfil_id)
            SELECT %s, %s, p.id FROM perfil p WHERE p.nombre = %s
            ON CONFLICT (usuario_id, perfil_id) DO NOTHING
            """,
            (str(_uuid.uuid4()), item["user_id"], config["role"]),
        )
        db.execute(
            f"""
            UPDATE {config['table']}
            SET {config['email_column']} = %s
            WHERE id = %s
            """,
            (login_email, item_id),
        )
        db.commit()
        return

    create_linked_person_user(entity, item_id, data)


def delete_linked_person_user(entity, item_id):
    item = get_entity(entity, item_id)
    if item is None or not item.get("user_id"):
        return

    db = get_db()
    db.execute("DELETE FROM usuario WHERE id = ?", (item["user_id"],))
    db.commit()


def entity_select_clause(entity):
    config = ENTITY_CONFIG[entity]
    alias_map = config.get("select_aliases", {})
    fields = ["id"]
    for field in config["fields"]:
        alias = alias_map.get(field)
        fields.append(f"{field} AS {alias}" if alias else field)
    if entity == "instructor" and "usuario_id AS user_id" not in fields:
        fields.append("usuario_id AS user_id")
    if entity == "instructor" and "area_id" not in fields:
        fields.append("area_id")
    if entity in {"aprendiz", "administrativo_persona"} and "usuario_id AS user_id" not in fields:
        fields.append("usuario_id AS user_id")
    return ", ".join(fields)


def get_entity(entity, item_id):
    if entity not in ENTITY_CONFIG or item_id is None:
        return None
    table = ENTITY_CONFIG[entity]["table"]
    return get_db().execute(
        f"SELECT {entity_select_clause(entity)} FROM {table} WHERE id = ?",
        (item_id,),
    ).fetchone()


def get_entities(entity, where=None, params=(), order_by="id DESC"):
    table = ENTITY_CONFIG[entity]["table"]
    sql = f"SELECT {entity_select_clause(entity)} FROM {table}"
    if where:
        sql += f" WHERE {where}"
    sql += f" ORDER BY {order_by}"
    return get_db().execute(sql, params).fetchall()


def get_admin_dashboard_data():
    db = get_db()
    total_active = db.execute("SELECT COUNT(*) AS total FROM usuario WHERE activo = TRUE").fetchone()["total"]
    total_roles = db.execute("SELECT COUNT(DISTINCT perfil_id) AS total FROM usuario_perfil").fetchone()["total"]
    total_regionales = db.execute("SELECT COUNT(*) AS total FROM regional").fetchone()["total"]
    total_centros = db.execute("SELECT COUNT(*) AS total FROM centro").fetchone()["total"]
    latest_users = db.execute(
        """
        SELECT u.nombre AS name, u.correo AS email,
               (SELECT p.nombre FROM usuario_perfil up
                JOIN perfil p ON p.id = up.perfil_id
                WHERE up.usuario_id = u.id LIMIT 1) AS role
        FROM usuario u
        ORDER BY u.creado_en DESC, u.id DESC
        LIMIT 3
        """
    ).fetchall()
    config = copy.deepcopy(DASHBOARDS["administrador"])
    config["metrics"][0]["value"] = str(total_active)
    config["metrics"][1]["value"] = str(total_regionales)
    config["metrics"][2]["value"] = str(total_roles)
    config["metrics"][3]["value"] = str(total_centros)
    config["table_title"] = "Ultimos usuarios registrados"
    config["table_headers"] = ["Nombre", "Rol", "Correo"]
    config["table_rows"] = [[row["name"], row["role"], row["email"]] for row in latest_users] or [["Sin registros", "-", "-"]]
    return config


def get_people_redirect_args(form_data, overrides=None):
    args = {
        "edit_entity": form_data.get("edit_entity"),
        "edit_id": parse_uuid(form_data.get("edit_id")),
    }
    args.update(overrides or {})
    return {key: value for key, value in args.items() if value not in (None, "")}


def normalize_people_context(args):
    edit_entity = args.get("edit_entity")
    edit_id = parse_uuid(args.get("edit_id"))
    if edit_entity not in PEOPLE_ENTITIES:
        edit_entity = None
        edit_id = None
    editing_item = get_entity(edit_entity, edit_id) if edit_entity and edit_id else None
    if edit_entity and editing_item is None:
        edit_entity = None
        edit_id = None
    return {
        "regionales": get_entities("regional", order_by="nombre ASC"),
        "coordinaciones": get_entities("coordinacion", order_by="nombre ASC"),
        "centros": get_entities("centro", order_by="nombre ASC"),
        "areas_academicas": get_entities("area", order_by="nombre ASC"),
        "instructores": get_entities("instructor", order_by="nombres ASC, apellidos ASC"),
        "aprendices": get_entities("aprendiz", order_by="nombres ASC, apellidos ASC"),
        "administrativos": get_entities("administrativo_persona", order_by="nombres ASC, apellidos ASC"),
        "edit_entity": edit_entity,
        "edit_id": edit_id,
        "editing_item": editing_item,
    }


def normalize_structure_context(args):
    regional_id = parse_uuid(args.get("regional_id"))
    centro_id = parse_uuid(args.get("centro_id"))
    coordinacion_id = parse_uuid(args.get("coordinacion_id"))
    sede_id = parse_uuid(args.get("sede_id"))
    edit_entity = args.get("edit_entity")
    edit_id = parse_uuid(args.get("edit_id"))

    regional = get_entity("regional", regional_id)
    if regional is None:
        regional_id = None
        centro_id = None
        coordinacion_id = None
        sede_id = None

    centro = get_entity("centro", centro_id)
    if centro is None or (regional_id and centro["regional_id"] != regional_id):
        centro = None
        centro_id = None
        coordinacion_id = None
        sede_id = None

    coordinacion = get_entity("coordinacion", coordinacion_id)
    if coordinacion is None or (centro_id and coordinacion["centro_id"] != centro_id):
        coordinacion = None
        coordinacion_id = None

    sede = get_entity("sede", sede_id)
    if sede is None or (centro_id and sede["centro_id"] != centro_id):
        sede = None
        sede_id = None

    if edit_entity not in ENTITY_CONFIG:
        edit_entity = None
        edit_id = None

    editing_item = get_entity(edit_entity, edit_id) if edit_entity and edit_id else None
    if edit_entity == "regional" and editing_item is None:
        edit_entity = None
        edit_id = None
    if edit_entity == "centro" and (editing_item is None or editing_item["regional_id"] != regional_id):
        edit_entity = None
        edit_id = None
    if edit_entity in {"coordinacion", "sede"} and (editing_item is None or editing_item["centro_id"] != centro_id):
        edit_entity = None
        edit_id = None
    if edit_entity not in STRUCTURE_ENTITIES and edit_entity is not None:
        edit_entity = None
        edit_id = None
    if edit_entity == "ambiente" and (editing_item is None or editing_item["sede_id"] != sede_id):
        edit_entity = None
        edit_id = None

    return {
        "selected_regional": regional,
        "selected_centro": centro,
        "selected_coordinacion": coordinacion,
        "selected_sede": sede,
        "areas_academicas": get_entities("area", order_by="nombre ASC"),
        "regionales": get_entities("regional", order_by="nombre ASC"),
        "centros": get_entities("centro", "regional_id = ?", (regional_id,), "nombre ASC") if regional_id else [],
        "coordinaciones": get_entities("coordinacion", "centro_id = ?", (centro_id,), "nombre ASC") if centro_id else [],
        "sedes": get_entities("sede", "centro_id = ?", (centro_id,), "nombre ASC") if centro_id else [],
        "ambientes": get_entities("ambiente", "sede_id = ?", (sede_id,), "nombre ASC") if sede_id else [],
        "edit_entity": edit_entity,
        "edit_id": edit_id,
        "editing_item": editing_item,
        "regional_id": regional_id,
        "centro_id": centro_id,
        "coordinacion_id": coordinacion_id,
        "sede_id": sede_id,
    }


def structure_redirect_args(form_data, overrides=None):
    args = {
        "regional_id": parse_uuid(form_data.get("regional_id")),
        "centro_id": parse_uuid(form_data.get("centro_id")),
        "coordinacion_id": parse_uuid(form_data.get("coordinacion_id")),
        "sede_id": parse_uuid(form_data.get("sede_id")),
    }
    args.update(overrides or {})
    return {key: value for key, value in args.items() if value}


def academic_redirect_args(form_data, overrides=None):
    args = {
        "red_id": parse_uuid(form_data.get("red_id")),
        "area_id": parse_uuid(form_data.get("area_id")),
        "programa_id": parse_uuid(form_data.get("programa_id")),
        "nivel_id": parse_uuid(form_data.get("nivel_id")),
        "proyecto_formativo_id": parse_uuid(form_data.get("proyecto_formativo_id")),
        "fase_id": parse_uuid(form_data.get("fase_id")),
        "actividad_proyecto_id": parse_uuid(form_data.get("actividad_proyecto_id")),
    }
    args.update(overrides or {})
    return {key: value for key, value in args.items() if value}


def normalize_academic_context(args):
    red_id = parse_uuid(args.get("red_id"))
    area_id = parse_uuid(args.get("area_id"))
    programa_id = parse_uuid(args.get("programa_id"))
    nivel_id = parse_uuid(args.get("nivel_id"))
    proyecto_formativo_id = parse_uuid(args.get("proyecto_formativo_id"))
    fase_id = parse_uuid(args.get("fase_id"))
    actividad_proyecto_id = parse_uuid(args.get("actividad_proyecto_id"))
    edit_entity = args.get("edit_entity")
    edit_id = parse_uuid(args.get("edit_id"))

    red = get_entity("red", red_id)
    if red is None:
        red_id = None
        area_id = None
        programa_id = None
    area = get_entity("area", area_id)
    if area is None or (red_id and area["red_id"] != red_id):
        area = None
        area_id = None
        programa_id = None
    programa = get_entity("programa", programa_id)
    if programa is None or (area_id and programa["area_id"] != area_id):
        programa = None
        programa_id = None
    nivel = get_entity("nivel", nivel_id)
    if nivel is None:
        nivel_id = None
    proyecto_formativo = get_entity("proyecto_formativo", proyecto_formativo_id)
    if proyecto_formativo is None:
        proyecto_formativo_id = None
        fase_id = None
    fase_proyecto = get_entity("fase_proyecto", fase_id)
    if fase_proyecto is None or (proyecto_formativo_id and fase_proyecto["proyecto_formativo_id"] != proyecto_formativo_id):
        fase_proyecto = None
        fase_id = None
        actividad_proyecto_id = None
    actividad_proyecto = get_entity("actividad_proyecto", actividad_proyecto_id)
    if actividad_proyecto is None or (fase_id and actividad_proyecto["fase_id"] != fase_id):
        actividad_proyecto = None
        actividad_proyecto_id = None
    if edit_entity not in ACADEMIC_ENTITIES:
        edit_entity = None
        edit_id = None
    editing_item = get_entity(edit_entity, edit_id) if edit_entity and edit_id else None
    if edit_entity == "area" and (editing_item is None or editing_item["red_id"] != red_id):
        edit_entity = None
        edit_id = None
    if edit_entity == "programa" and (editing_item is None or editing_item["area_id"] != area_id):
        edit_entity = None
        edit_id = None
    if edit_entity == "ficha" and (editing_item is None or editing_item["programa_id"] != programa_id):
        edit_entity = None
        edit_id = None
    if edit_entity == "fase_proyecto" and (editing_item is None or editing_item["proyecto_formativo_id"] != proyecto_formativo_id):
        edit_entity = None
        edit_id = None
    if edit_entity == "actividad_proyecto" and (editing_item is None or editing_item["fase_id"] != fase_id):
        edit_entity = None
        edit_id = None
    if edit_entity == "actividad_aprendizaje" and (editing_item is None or editing_item["actividad_proyecto_id"] != actividad_proyecto_id):
        edit_entity = None
        edit_id = None
    if edit_entity in {"red", "nivel", "proyecto_formativo"} and editing_item is None:
        edit_entity = None
        edit_id = None

    fichas = []
    if programa_id:
        fichas = get_db().execute(
            """
            SELECT f.id, f.numero, f.programa_formacion_id AS programa_id,
                   f.proyecto_formativo_id,
                   f.coordinacion_id, f.instructor_id,
                   pf.nombre AS proyecto_formativo_nombre,
                   c.nombre AS coordinacion_nombre,
                   i.nombres || ' ' || i.apellidos AS instructor_nombre
            FROM ficha_formacion f
            LEFT JOIN proyecto_formativo pf ON pf.id = f.proyecto_formativo_id
            JOIN coordinacion c ON c.id = f.coordinacion_id
            LEFT JOIN instructor i ON i.id = f.instructor_id
            WHERE f.programa_formacion_id = ?
            ORDER BY f.numero ASC
            """,
            (programa_id,),
        ).fetchall()

    instructores_area = []
    if programa:
        instructores_area = get_db().execute(
            """
            SELECT id, documento, nombres, apellidos, correo AS email,
                   area_id, centro_id
            FROM instructor
            WHERE area_id = ?
            ORDER BY nombres ASC, apellidos ASC
            """,
            (programa["area_id"],),
        ).fetchall()

    return {
        "redes": get_entities("red", order_by="nombre ASC"),
        "areas": get_entities("area", "red_conocimiento_id = ?", (red_id,), "nombre ASC") if red_id else [],
        "niveles": get_entities("nivel", order_by="nombre ASC"),
        "programas": get_entities("programa", "area_id = ?", (area_id,), "nombre ASC") if area_id else [],
        "fichas": fichas,
        "coordinaciones_disponibles": get_entities("coordinacion", order_by="nombre ASC"),
        "instructores_area": instructores_area,
        "proyectos_formativos": get_entities("proyecto_formativo", order_by="codigo ASC, nombre ASC"),
        "fases_proyecto": get_entities("fase_proyecto", "proyecto_formativo_id = ?", (proyecto_formativo_id,), "nombre ASC") if proyecto_formativo_id else [],
        "actividades_proyecto": get_entities("actividad_proyecto", "fase_proyecto_id = ?", (fase_id,), "nombre ASC") if fase_id else [],
        "actividades_aprendizaje": get_entities("actividad_aprendizaje", "actividad_proyecto_id = ?", (actividad_proyecto_id,), "nombre ASC") if actividad_proyecto_id else [],
        "selected_red": red,
        "selected_area": area,
        "selected_programa": programa,
        "selected_nivel": nivel,
        "selected_proyecto_formativo": proyecto_formativo,
        "selected_fase_proyecto": fase_proyecto,
        "selected_actividad_proyecto": actividad_proyecto,
        "edit_entity": edit_entity,
        "edit_id": edit_id,
        "editing_item": editing_item,
        "red_id": red_id,
        "area_id": area_id,
        "programa_id": programa_id,
        "nivel_id": nivel_id,
        "proyecto_formativo_id": proyecto_formativo_id,
        "fase_id": fase_id,
        "actividad_proyecto_id": actividad_proyecto_id,
    }


def entity_form_data(entity, form):
    data = {}
    form_to_db = ENTITY_CONFIG[entity].get("form_to_db", {})
    for field in ENTITY_CONFIG[entity]["fields"]:
        form_field = next((name for name, db_name in form_to_db.items() if db_name == field), field)
        values = [value.strip() for value in form.getlist(form_field)]
        raw = next((value for value in reversed(values) if value != ""), "")
        if field.endswith("_id"):
            data[field] = raw or None
        elif field == "capacidad":
            data[field] = parse_int(raw) if raw else None
        else:
            data[field] = raw
    return data


def validate_entity_payload(entity, data):
    config = ENTITY_CONFIG[entity]
    for field in config["required"]:
        if data.get(field) in (None, ""):
            return f"El campo {field.replace('_', ' ')} es obligatorio."
    if entity == "ambiente" and data["capacidad"] is not None and data["capacidad"] < 0:
        return "La capacidad no puede ser negativa."
    if entity == "instructor" and get_entity("centro", data["centro_id"]) is None:
        return "El centro de formación seleccionado no existe."
    if entity == "instructor" and data.get("area_id") is not None and get_entity("area", data["area_id"]) is None:
        return "El área académica seleccionada no existe."
    if entity == "aprendiz" and get_entity("regional", data["regional_id"]) is None:
        return "La regional seleccionada no existe."
    if entity == "ficha" and data["instructor_id"] in ("", None):
        data["instructor_id"] = None
    return None


def validate_academic_payload(entity, data):
    validation_error = validate_entity_payload(entity, data)
    if validation_error:
        return validation_error
    if entity == "programa":
        if data.get("area_id") is None or data.get("nivel_formacion_id") is None:
            return "El programa debe tener área y nivel de formación."
        if get_entity("area", data["area_id"]) is None:
            return "El área seleccionada no existe."
        if get_entity("nivel", data["nivel_formacion_id"]) is None:
            return "El nivel de formación seleccionado no existe."
    if entity == "ficha":
        programa = get_entity("programa", data["programa_formacion_id"])
        if programa is None:
            return "El programa seleccionado no existe."
        if get_entity("proyecto_formativo", data["proyecto_formativo_id"]) is None:
            return "El proyecto formativo seleccionado no existe."
        coordinacion = get_entity("coordinacion", data["coordinacion_id"])
        if coordinacion is None:
            return "La coordinación seleccionada no existe."
        if data.get("instructor_id"):
            instructor = get_entity("instructor", data["instructor_id"])
            if instructor is None:
                return "El instructor seleccionado no existe."
            if not instructor.get("area_id") or instructor["area_id"] != programa["area_id"]:
                return "El instructor asignado debe pertenecer a la misma área del programa."
            centro_coordinacion = get_entity("centro", coordinacion["centro_id"])
            if centro_coordinacion is None or instructor["centro_id"] != centro_coordinacion["id"]:
                return "El instructor asignado debe pertenecer al centro de formación de la coordinación seleccionada."
    if entity == "fase_proyecto" and get_entity("proyecto_formativo", data["proyecto_formativo_id"]) is None:
        return "El proyecto formativo seleccionado no existe."
    if entity == "actividad_proyecto" and get_entity("fase_proyecto", data["fase_proyecto_id"]) is None:
        return "La fase seleccionada no existe."
    if entity == "actividad_aprendizaje" and get_entity("actividad_proyecto", data["actividad_proyecto_id"]) is None:
        return "La actividad de proyecto seleccionada no existe."
    return None


def insert_entity(entity, data):
    config = ENTITY_CONFIG[entity]
    columns = ", ".join(config["fields"])
    placeholders = ", ".join(["?"] * len(config["fields"]))
    values = tuple(data[field] for field in config["fields"])
    cursor = get_db().execute(
        f"INSERT INTO {config['table']} ({columns}) VALUES ({placeholders}) RETURNING id",
        values,
    )
    get_db().commit()
    return cursor.fetchone()["id"]


def update_entity(entity, item_id, data):
    config = ENTITY_CONFIG[entity]
    assignments = ", ".join([f"{field} = ?" for field in config["fields"]])
    values = tuple(data[field] for field in config["fields"]) + (item_id,)
    get_db().execute(f"UPDATE {config['table']} SET {assignments} WHERE id = ?", values)
    get_db().commit()


def delete_entity(entity, item_id):
    get_db().execute(f"DELETE FROM {ENTITY_CONFIG[entity]['table']} WHERE id = ?", (item_id,))
    get_db().commit()
