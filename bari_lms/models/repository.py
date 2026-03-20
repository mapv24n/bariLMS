import copy

import psycopg
from flask import current_app, g
from psycopg.rows import dict_row
from werkzeug.security import generate_password_hash

from bari_lms.config import DASHBOARDS, DEFAULT_LEVELS, DEFAULT_USERS

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
        "fields": ["id_regional", "nombre"],
        "required": ["id_regional", "nombre"],
        "context_key": "centro_id",
        "select_aliases": {"id_regional": "regional_id"},
        "form_to_db": {"regional_id": "id_regional"},
    },
    "coordinacion": {
        "table": "coordinacion",
        "label": "Coordinación",
        "parent_key": "centro_id",
        "fields": ["id_centro", "nombre"],
        "required": ["id_centro", "nombre"],
        "context_key": "coordinacion_id",
        "select_aliases": {"id_centro": "centro_id"},
        "form_to_db": {"centro_id": "id_centro"},
    },
    "sede": {
        "table": "sede",
        "label": "Sede",
        "parent_key": "centro_id",
        "fields": ["id_centro", "nombre"],
        "required": ["id_centro", "nombre"],
        "context_key": "sede_id",
        "select_aliases": {"id_centro": "centro_id"},
        "form_to_db": {"centro_id": "id_centro"},
    },
    "instructor": {
        "table": "instructor",
        "label": "Instructor",
        "parent_key": "centro_id",
        "fields": ["id_centro", "id_area", "documento", "nombres", "apellidos", "correo"],
        "required": ["id_centro", "documento", "nombres", "apellidos"],
        "context_key": "centro_id",
        "select_aliases": {
            "id_centro": "centro_id",
            "id_area": "area_id",
            "correo": "email",
            "id_usuario": "user_id",
        },
        "form_to_db": {"centro_id": "id_centro", "area_id": "id_area", "email": "correo"},
    },
    "aprendiz": {
        "table": "aprendiz",
        "label": "Aprendiz",
        "parent_key": "regional_id",
        "fields": ["id_regional", "documento", "nombres", "apellidos", "correo", "ficha"],
        "required": ["id_regional", "documento", "nombres", "apellidos"],
        "context_key": "regional_id",
        "select_aliases": {"id_regional": "regional_id", "correo": "email", "id_usuario": "user_id"},
        "form_to_db": {"regional_id": "id_regional"},
    },
    "ambiente": {
        "table": "ambiente",
        "label": "Ambiente",
        "parent_key": "sede_id",
        "fields": ["id_sede", "nombre", "capacidad"],
        "required": ["id_sede", "nombre"],
        "context_key": "sede_id",
        "select_aliases": {"id_sede": "sede_id"},
        "form_to_db": {"sede_id": "id_sede"},
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
        "fields": ["id_red_conocimiento", "nombre"],
        "required": ["id_red_conocimiento", "nombre"],
        "context_key": "area_id",
        "select_aliases": {"id_red_conocimiento": "red_id"},
        "form_to_db": {"red_id": "id_red_conocimiento"},
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
        "fields": ["id_area", "id_nivel_formacion", "nombre"],
        "required": ["id_area", "id_nivel_formacion", "nombre"],
        "context_key": "programa_id",
        "select_aliases": {"id_area": "area_id", "id_nivel_formacion": "nivel_id"},
        "form_to_db": {"area_id": "id_area", "nivel_id": "id_nivel_formacion"},
    },
    "ficha": {
        "table": "ficha_formacion",
        "label": "Ficha de formación",
        "parent_key": "programa_id",
        "fields": ["numero", "id_programa_formacion", "id_proyecto_formativo", "id_coordinacion", "id_instructor"],
        "required": ["numero", "id_programa_formacion", "id_proyecto_formativo", "id_coordinacion"],
        "context_key": "programa_id",
        "select_aliases": {
            "id_programa_formacion": "programa_id",
            "id_proyecto_formativo": "proyecto_formativo_id",
            "id_coordinacion": "coordinacion_id",
            "id_instructor": "instructor_id",
        },
        "form_to_db": {
            "programa_id": "id_programa_formacion",
            "proyecto_formativo_id": "id_proyecto_formativo",
            "coordinacion_id": "id_coordinacion",
            "instructor_id": "id_instructor",
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
        "fields": ["id_proyecto_formativo", "nombre"],
        "required": ["id_proyecto_formativo", "nombre"],
        "context_key": "fase_id",
        "select_aliases": {"id_proyecto_formativo": "proyecto_formativo_id"},
        "form_to_db": {"proyecto_formativo_id": "id_proyecto_formativo"},
    },
    "actividad_proyecto": {
        "table": "actividad_proyecto",
        "label": "Actividad del proyecto",
        "parent_key": "fase_id",
        "fields": ["id_fase_proyecto", "nombre"],
        "required": ["id_fase_proyecto", "nombre"],
        "context_key": "fase_id",
        "select_aliases": {"id_fase_proyecto": "fase_id"},
        "form_to_db": {"fase_id": "id_fase_proyecto"},
    },
    "actividad_aprendizaje": {
        "table": "actividad_aprendizaje",
        "label": "Actividad de aprendizaje",
        "parent_key": "actividad_proyecto_id",
        "fields": ["id_actividad_proyecto", "nombre"],
        "required": ["id_actividad_proyecto", "nombre"],
        "context_key": "actividad_proyecto_id",
        "select_aliases": {"id_actividad_proyecto": "actividad_proyecto_id"},
        "form_to_db": {"actividad_proyecto_id": "id_actividad_proyecto"},
    },
    "administrativo_persona": {
        "table": "personal_administrativo",
        "label": "Personal administrativo",
        "parent_key": "centro_id",
        "fields": ["id_centro", "documento", "nombres", "apellidos", "correo", "cargo"],
        "required": ["id_centro", "documento", "nombres", "apellidos", "cargo"],
        "context_key": "centro_id",
        "select_aliases": {"id_centro": "centro_id", "correo": "email", "id_usuario": "user_id"},
        "form_to_db": {"centro_id": "id_centro"},
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
    "centro": {"regional_id": "id_regional"},
    "coordinacion": {"centro_id": "id_centro"},
    "sede": {"centro_id": "id_centro"},
    "instructor": {
        "coordinacion_id": "id_coordinacion",
        "centro_id": "id_centro",
        "email": "correo",
        "user_id": "id_usuario",
    },
    "aprendiz": {"coordinacion_id": "id_coordinacion", "regional_id": "id_regional"},
    "ambiente": {"sede_id": "id_sede"},
}

PERSON_USER_CONFIG = {
    "instructor": {
        "role": "Instructor",
        "email_prefix": "instructor",
        "table": "instructor",
        "email_column": "correo",
        "user_column": "id_usuario",
    },
    "aprendiz": {
        "role": "Aprendiz",
        "email_prefix": "aprendiz",
        "table": "aprendiz",
        "email_column": "correo",
        "user_column": "id_usuario",
    },
    "administrativo_persona": {
        "role": "Administrativo",
        "email_prefix": "administrativo",
        "table": "personal_administrativo",
        "email_column": "correo",
        "user_column": "id_usuario",
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


def get_db():
    if "db" not in g:
        connection = psycopg.connect(
            host=current_app.config["PGHOST"],
            port=current_app.config["PGPORT"],
            dbname=current_app.config["PGDATABASE"],
            user=current_app.config["PGUSER"],
            password=current_app.config["PGPASSWORD"],
        )
        g.db = PostgresConnection(connection)
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


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
            id SERIAL PRIMARY KEY,
            correo TEXT UNIQUE NOT NULL,
            contrasena_hash TEXT NOT NULL,
            rol TEXT NOT NULL,
            nombre TEXT NOT NULL,
            activo BOOLEAN NOT NULL DEFAULT TRUE,
            creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.execute("CREATE TABLE IF NOT EXISTS regional (id SERIAL PRIMARY KEY, nombre TEXT NOT NULL UNIQUE)")
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS centro (
            id SERIAL PRIMARY KEY,
            id_regional INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_regional) REFERENCES regional(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS coordinacion (
            id SERIAL PRIMARY KEY,
            id_centro INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_centro) REFERENCES centro(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS sede (
            id SERIAL PRIMARY KEY,
            id_centro INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_centro) REFERENCES centro(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS instructor (
            id SERIAL PRIMARY KEY,
            id_centro INTEGER NOT NULL,
            documento TEXT NOT NULL,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            correo TEXT,
            id_usuario INTEGER,
            FOREIGN KEY (id_centro) REFERENCES centro(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS aprendiz (
            id SERIAL PRIMARY KEY,
            id_regional INTEGER,
            documento TEXT NOT NULL,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            correo TEXT,
            id_usuario INTEGER,
            ficha TEXT,
            FOREIGN KEY (id_regional) REFERENCES regional(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS personal_administrativo (
            id SERIAL PRIMARY KEY,
            id_centro INTEGER NOT NULL,
            documento TEXT NOT NULL,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            correo TEXT,
            cargo TEXT NOT NULL,
            id_usuario INTEGER,
            FOREIGN KEY (id_centro) REFERENCES centro(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS ambiente (
            id SERIAL PRIMARY KEY,
            id_sede INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            capacidad INTEGER,
            FOREIGN KEY (id_sede) REFERENCES sede(id) ON DELETE CASCADE
        )
        """
    )
    db.execute("CREATE TABLE IF NOT EXISTS red_conocimiento (id SERIAL PRIMARY KEY, nombre TEXT NOT NULL UNIQUE)")
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS area (
            id SERIAL PRIMARY KEY,
            id_red_conocimiento INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_red_conocimiento) REFERENCES red_conocimiento(id) ON DELETE CASCADE
        )
        """
    )
    db.execute("CREATE TABLE IF NOT EXISTS nivel_formacion (id SERIAL PRIMARY KEY, nombre TEXT NOT NULL UNIQUE)")
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS programa_formacion (
            id SERIAL PRIMARY KEY,
            id_area INTEGER NOT NULL,
            id_nivel_formacion INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_area) REFERENCES area(id) ON DELETE CASCADE,
            FOREIGN KEY (id_nivel_formacion) REFERENCES nivel_formacion(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS ficha_formacion (
            id SERIAL PRIMARY KEY,
            numero TEXT NOT NULL UNIQUE,
            id_programa_formacion INTEGER NOT NULL,
            id_proyecto_formativo INTEGER,
            id_coordinacion INTEGER NOT NULL,
            id_instructor INTEGER,
            FOREIGN KEY (id_programa_formacion) REFERENCES programa_formacion(id) ON DELETE CASCADE,
            FOREIGN KEY (id_proyecto_formativo) REFERENCES proyecto_formativo(id) ON DELETE SET NULL,
            FOREIGN KEY (id_coordinacion) REFERENCES coordinacion(id) ON DELETE CASCADE,
            FOREIGN KEY (id_instructor) REFERENCES instructor(id) ON DELETE SET NULL
        )
        """
    )
    db.execute("CREATE TABLE IF NOT EXISTS proyecto_formativo (id SERIAL PRIMARY KEY, codigo TEXT NOT NULL UNIQUE, nombre TEXT NOT NULL)")
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS fase_proyecto (
            id SERIAL PRIMARY KEY,
            id_proyecto_formativo INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_proyecto_formativo) REFERENCES proyecto_formativo(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS actividad_proyecto (
            id SERIAL PRIMARY KEY,
            id_fase_proyecto INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_fase_proyecto) REFERENCES fase_proyecto(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS actividad_aprendizaje (
            id SERIAL PRIMARY KEY,
            id_actividad_proyecto INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_actividad_proyecto) REFERENCES actividad_proyecto(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS guia_aprendizaje (
            id SERIAL PRIMARY KEY,
            id_actividad_aprendizaje INTEGER NOT NULL UNIQUE,
            url TEXT NOT NULL,
            subido_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_actividad_aprendizaje) REFERENCES actividad_aprendizaje(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS evidencia_aprendizaje (
            id SERIAL PRIMARY KEY,
            id_actividad_aprendizaje INTEGER NOT NULL UNIQUE,
            descripcion TEXT,
            creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_actividad_aprendizaje) REFERENCES actividad_aprendizaje(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS entrega_evidencia (
            id SERIAL PRIMARY KEY,
            id_evidencia_aprendizaje INTEGER NOT NULL,
            id_usuario INTEGER NOT NULL,
            url TEXT,
            calificacion NUMERIC(5,2),
            observaciones TEXT,
            entregado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_evidencia_aprendizaje) REFERENCES evidencia_aprendizaje(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS seccion_actividad (
            id SERIAL PRIMARY KEY,
            id_actividad_aprendizaje INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            archivo_url TEXT,
            archivo_tipo TEXT,
            fecha_inicio DATE,
            fecha_fin DATE,
            orden INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (id_actividad_aprendizaje) REFERENCES actividad_aprendizaje(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS sub_seccion_actividad (
            id SERIAL PRIMARY KEY,
            id_seccion INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            archivo_url TEXT,
            archivo_tipo TEXT,
            fecha_inicio DATE,
            fecha_fin DATE,
            orden INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (id_seccion) REFERENCES seccion_actividad(id) ON DELETE CASCADE
        )
        """
    )
    db.commit()

    instructor_genero_columns = get_table_columns("instructor")
    if "genero" not in instructor_genero_columns:
        db.execute("ALTER TABLE instructor ADD COLUMN IF NOT EXISTS genero TEXT NOT NULL DEFAULT 'M'")
        db.commit()

    actividad_columns = get_table_columns("actividad_aprendizaje")
    if "descripcion" not in actividad_columns:
        db.execute("ALTER TABLE actividad_aprendizaje ADD COLUMN IF NOT EXISTS descripcion TEXT")
        db.commit()
    if "fecha_inicio" not in actividad_columns:
        db.execute("ALTER TABLE actividad_aprendizaje ADD COLUMN IF NOT EXISTS fecha_inicio DATE")
        db.commit()
    if "fecha_fin" not in actividad_columns:
        db.execute("ALTER TABLE actividad_aprendizaje ADD COLUMN IF NOT EXISTS fecha_fin DATE")
        db.commit()

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS ficha_instructor_competencia (
            id SERIAL PRIMARY KEY,
            id_ficha INTEGER NOT NULL REFERENCES ficha_formacion(id) ON DELETE CASCADE,
            id_instructor INTEGER NOT NULL REFERENCES instructor(id) ON DELETE CASCADE,
            UNIQUE (id_ficha, id_instructor)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS guia_actividad_proyecto (
            id SERIAL PRIMARY KEY,
            id_actividad_proyecto INTEGER NOT NULL,
            nombre TEXT,
            url TEXT NOT NULL,
            subido_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_actividad_proyecto) REFERENCES actividad_proyecto(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS asistencia_aprendiz (
            id SERIAL PRIMARY KEY,
            id_ficha INTEGER NOT NULL,
            id_aprendiz INTEGER NOT NULL,
            fecha DATE NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Presente',
            FOREIGN KEY (id_ficha) REFERENCES ficha_formacion(id) ON DELETE CASCADE,
            FOREIGN KEY (id_aprendiz) REFERENCES aprendiz(id) ON DELETE CASCADE,
            UNIQUE(id_ficha, id_aprendiz, fecha)
        )
        """
    )
    db.commit()

    # Columna orden en actividad_aprendizaje
    act_apr_cols = get_table_columns("actividad_aprendizaje")
    if "orden" not in act_apr_cols:
        db.execute("ALTER TABLE actividad_aprendizaje ADD COLUMN IF NOT EXISTS orden INTEGER NOT NULL DEFAULT 0")
        db.commit()

    # Nuevas columnas en guia_actividad_proyecto
    guia_ap_cols = get_table_columns("guia_actividad_proyecto")
    if "descripcion" not in guia_ap_cols:
        db.execute("ALTER TABLE guia_actividad_proyecto ADD COLUMN IF NOT EXISTS descripcion TEXT")
        db.commit()
    if "orden" not in guia_ap_cols:
        db.execute("ALTER TABLE guia_actividad_proyecto ADD COLUMN IF NOT EXISTS orden INTEGER NOT NULL DEFAULT 0")
        db.commit()

    instructor_columns = get_table_columns("instructor")
    if "id_centro" not in instructor_columns:
        db.execute("ALTER TABLE instructor ADD COLUMN IF NOT EXISTS id_centro INTEGER")
        db.commit()
        instructor_columns.add("id_centro")
    if "id_usuario" not in instructor_columns:
        db.execute("ALTER TABLE instructor ADD COLUMN IF NOT EXISTS id_usuario INTEGER")
        db.commit()
        instructor_columns.add("id_usuario")
    if "id_area" not in instructor_columns:
        db.execute("ALTER TABLE instructor ADD COLUMN IF NOT EXISTS id_area INTEGER")
        db.commit()
        instructor_columns.add("id_area")
    if "id_coordinacion" in instructor_columns:
        db.execute(
            """
            UPDATE instructor i
            SET id_centro = c.id_centro
            FROM coordinacion c
            WHERE (i.id_centro IS NULL OR i.id_centro = 0) AND i.id_coordinacion = c.id
            """
        )
        db.commit()
        db.execute("ALTER TABLE instructor DROP CONSTRAINT IF EXISTS instructor_id_coordinacion_fkey")
        db.commit()
        db.execute("ALTER TABLE instructor DROP COLUMN IF EXISTS id_coordinacion")
        db.commit()
    if not constraint_exists("instructor", "instructor_id_centro_fkey"):
        db.execute(
            """
            ALTER TABLE instructor
            ADD CONSTRAINT instructor_id_centro_fkey
            FOREIGN KEY (id_centro) REFERENCES centro(id) ON DELETE CASCADE
            """
        )
        db.commit()
    db.execute("ALTER TABLE instructor ALTER COLUMN id_centro SET NOT NULL")
    db.commit()

    aprendiz_columns = get_table_columns("aprendiz")
    if "id_regional" not in aprendiz_columns:
        db.execute("ALTER TABLE aprendiz ADD COLUMN IF NOT EXISTS id_regional INTEGER")
        db.commit()
        aprendiz_columns.add("id_regional")
    if "correo" not in aprendiz_columns:
        db.execute("ALTER TABLE aprendiz ADD COLUMN IF NOT EXISTS correo TEXT")
        db.commit()
        aprendiz_columns.add("correo")
    if "id_usuario" not in aprendiz_columns:
        db.execute("ALTER TABLE aprendiz ADD COLUMN IF NOT EXISTS id_usuario INTEGER")
        db.commit()
        aprendiz_columns.add("id_usuario")
    if "id_coordinacion" in aprendiz_columns:
        db.execute(
            """
            UPDATE aprendiz a
            SET id_regional = c.id_regional
            FROM coordinacion co
            JOIN centro c ON c.id = co.id_centro
            WHERE a.id_regional IS NULL AND a.id_coordinacion = co.id
            """
        )
        db.commit()
        db.execute("ALTER TABLE aprendiz DROP CONSTRAINT IF EXISTS aprendiz_id_coordinacion_fkey")
        db.commit()
        db.execute("ALTER TABLE aprendiz DROP COLUMN IF EXISTS id_coordinacion")
        db.commit()
    if not constraint_exists("aprendiz", "aprendiz_id_regional_fkey"):
        db.execute(
            """
            ALTER TABLE aprendiz
            ADD CONSTRAINT aprendiz_id_regional_fkey
            FOREIGN KEY (id_regional) REFERENCES regional(id) ON DELETE CASCADE
            """
        )
        db.commit()
    db.execute("ALTER TABLE aprendiz ALTER COLUMN id_regional SET NOT NULL")
    db.commit()

    ficha_columns = get_table_columns("ficha_formacion")
    if "id_proyecto_formativo" not in ficha_columns:
        db.execute("ALTER TABLE ficha_formacion ADD COLUMN IF NOT EXISTS id_proyecto_formativo INTEGER")
        db.commit()

    user_count = db.execute("SELECT COUNT(*) AS total FROM usuario").fetchone()["total"]
    if user_count == 0:
        for user in DEFAULT_USERS:
            db.execute(
                """
                INSERT INTO usuario (correo, contrasena_hash, rol, nombre, activo)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user["email"],
                    generate_password_hash(user["password"]),
                    user["role"],
                    user["name"],
                    user["active"],
                ),
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
        SELECT id, correo AS email, rol AS role, nombre AS name, activo AS active,
               creado_en AS created_at, contrasena_hash AS password_hash
        FROM usuario
        WHERE lower(correo) = lower(?)
        """,
        (email,),
    ).fetchone()


def get_user_by_id(user_id):
    return get_db().execute(
        """
        SELECT id, correo AS email, rol AS role, nombre AS name, activo AS active, creado_en AS created_at
        FROM usuario
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()


def get_all_users():
    return get_db().execute(
        """
        SELECT id, correo AS email, rol AS role, nombre AS name, activo AS active, creado_en AS created_at
        FROM usuario
        ORDER BY creado_en DESC, id DESC
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

    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO usuario (correo, contrasena_hash, rol, nombre, activo)
        VALUES (?, ?, ?, ?, TRUE)
        RETURNING id
        """,
        (
            login_email,
            generate_password_hash(data["documento"]),
            config["role"],
            person_full_name(data),
        ),
    )
    user_id = cursor.fetchone()["id"]
    db.execute(
        f"""
        UPDATE {config['table']}
        SET {config['email_column']} = ?, {config['user_column']} = ?
        WHERE id = ?
        """,
        (login_email, user_id, item_id),
    )
    db.commit()
    return user_id


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

        db.execute(
            """
            UPDATE usuario
            SET correo = ?, contrasena_hash = ?, rol = ?, nombre = ?, activo = TRUE
            WHERE id = ?
            """,
            (
                login_email,
                generate_password_hash(data["documento"]),
                config["role"],
                person_full_name(data),
                item["user_id"],
            ),
        )
        db.execute(
            f"""
            UPDATE {config['table']}
            SET {config['email_column']} = ?
            WHERE id = ?
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
    if entity == "instructor" and "id_usuario AS user_id" not in fields:
        fields.append("id_usuario AS user_id")
    if entity == "instructor" and "id_area AS area_id" not in fields:
        fields.append("id_area AS area_id")
    if entity in {"aprendiz", "administrativo_persona"} and "id_usuario AS user_id" not in fields:
        fields.append("id_usuario AS user_id")
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
    total_roles = db.execute("SELECT COUNT(DISTINCT rol) AS total FROM usuario").fetchone()["total"]
    total_regionales = db.execute("SELECT COUNT(*) AS total FROM regional").fetchone()["total"]
    total_centros = db.execute("SELECT COUNT(*) AS total FROM centro").fetchone()["total"]
    latest_users = db.execute(
        """
        SELECT nombre AS name, rol AS role, correo AS email
        FROM usuario
        ORDER BY creado_en DESC, id DESC
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
        "edit_id": parse_int(form_data.get("edit_id")),
    }
    args.update(overrides or {})
    return {key: value for key, value in args.items() if value not in (None, "")}


def normalize_people_context(args):
    edit_entity = args.get("edit_entity")
    edit_id = parse_int(args.get("edit_id"))
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
    regional_id = parse_int(args.get("regional_id"))
    centro_id = parse_int(args.get("centro_id"))
    coordinacion_id = parse_int(args.get("coordinacion_id"))
    sede_id = parse_int(args.get("sede_id"))
    edit_entity = args.get("edit_entity")
    edit_id = parse_int(args.get("edit_id"))

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
        "centros": get_entities("centro", "id_regional = ?", (regional_id,), "nombre ASC") if regional_id else [],
        "coordinaciones": get_entities("coordinacion", "id_centro = ?", (centro_id,), "nombre ASC") if centro_id else [],
        "sedes": get_entities("sede", "id_centro = ?", (centro_id,), "nombre ASC") if centro_id else [],
        "ambientes": get_entities("ambiente", "id_sede = ?", (sede_id,), "nombre ASC") if sede_id else [],
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
        "regional_id": parse_int(form_data.get("regional_id")),
        "centro_id": parse_int(form_data.get("centro_id")),
        "coordinacion_id": parse_int(form_data.get("coordinacion_id")),
        "sede_id": parse_int(form_data.get("sede_id")),
    }
    args.update(overrides or {})
    return {key: value for key, value in args.items() if value}


def academic_redirect_args(form_data, overrides=None):
    args = {
        "red_id": parse_int(form_data.get("red_id")),
        "area_id": parse_int(form_data.get("area_id")),
        "programa_id": parse_int(form_data.get("programa_id")),
        "nivel_id": parse_int(form_data.get("nivel_id")),
        "proyecto_formativo_id": parse_int(form_data.get("proyecto_formativo_id")),
        "fase_id": parse_int(form_data.get("fase_id")),
        "actividad_proyecto_id": parse_int(form_data.get("actividad_proyecto_id")),
    }
    args.update(overrides or {})
    return {key: value for key, value in args.items() if value}


def normalize_academic_context(args):
    red_id = parse_int(args.get("red_id"))
    area_id = parse_int(args.get("area_id"))
    programa_id = parse_int(args.get("programa_id"))
    nivel_id = parse_int(args.get("nivel_id"))
    proyecto_formativo_id = parse_int(args.get("proyecto_formativo_id"))
    fase_id = parse_int(args.get("fase_id"))
    actividad_proyecto_id = parse_int(args.get("actividad_proyecto_id"))
    edit_entity = args.get("edit_entity")
    edit_id = parse_int(args.get("edit_id"))

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
            SELECT f.id, f.numero, f.id_programa_formacion AS programa_id,
                   f.id_proyecto_formativo AS proyecto_formativo_id,
                   f.id_coordinacion AS coordinacion_id, f.id_instructor AS instructor_id,
                   pf.nombre AS proyecto_formativo_nombre,
                   c.nombre AS coordinacion_nombre,
                   i.nombres || ' ' || i.apellidos AS instructor_nombre
            FROM ficha_formacion f
            LEFT JOIN proyecto_formativo pf ON pf.id = f.id_proyecto_formativo
            JOIN coordinacion c ON c.id = f.id_coordinacion
            LEFT JOIN instructor i ON i.id = f.id_instructor
            WHERE f.id_programa_formacion = ?
            ORDER BY f.numero ASC
            """,
            (programa_id,),
        ).fetchall()

    instructores_area = []
    if programa:
        instructores_area = get_db().execute(
            """
            SELECT id, documento, nombres, apellidos, correo AS email,
                   id_area AS area_id, id_centro AS centro_id
            FROM instructor
            WHERE id_area = ?
            ORDER BY nombres ASC, apellidos ASC
            """,
            (programa["area_id"],),
        ).fetchall()

    return {
        "redes": get_entities("red", order_by="nombre ASC"),
        "areas": get_entities("area", "id_red_conocimiento = ?", (red_id,), "nombre ASC") if red_id else [],
        "niveles": get_entities("nivel", order_by="nombre ASC"),
        "programas": get_entities("programa", "id_area = ?", (area_id,), "nombre ASC") if area_id else [],
        "fichas": fichas,
        "coordinaciones_disponibles": get_entities("coordinacion", order_by="nombre ASC"),
        "instructores_area": instructores_area,
        "proyectos_formativos": get_entities("proyecto_formativo", order_by="codigo ASC, nombre ASC"),
        "fases_proyecto": get_entities("fase_proyecto", "id_proyecto_formativo = ?", (proyecto_formativo_id,), "nombre ASC") if proyecto_formativo_id else [],
        "actividades_proyecto": get_entities("actividad_proyecto", "id_fase_proyecto = ?", (fase_id,), "nombre ASC") if fase_id else [],
        "actividades_aprendizaje": get_entities("actividad_aprendizaje", "id_actividad_proyecto = ?", (actividad_proyecto_id,), "nombre ASC") if actividad_proyecto_id else [],
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
        if field.endswith("_id") or field.startswith("id_"):
            data[field] = parse_int(raw)
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
    if entity == "instructor" and get_entity("centro", data["id_centro"]) is None:
        return "El centro de formación seleccionado no existe."
    if entity == "instructor" and data.get("id_area") is not None and get_entity("area", data["id_area"]) is None:
        return "El área académica seleccionada no existe."
    if entity == "aprendiz" and get_entity("regional", data["id_regional"]) is None:
        return "La regional seleccionada no existe."
    if entity == "ficha" and data["id_instructor"] in ("", None):
        data["id_instructor"] = None
    return None


def validate_academic_payload(entity, data):
    validation_error = validate_entity_payload(entity, data)
    if validation_error:
        return validation_error
    if entity == "programa":
        if data.get("id_area") is None or data.get("id_nivel_formacion") is None:
            return "El programa debe tener área y nivel de formación."
        if get_entity("area", data["id_area"]) is None:
            return "El área seleccionada no existe."
        if get_entity("nivel", data["id_nivel_formacion"]) is None:
            return "El nivel de formación seleccionado no existe."
    if entity == "ficha":
        programa = get_entity("programa", data["id_programa_formacion"])
        if programa is None:
            return "El programa seleccionado no existe."
        if get_entity("proyecto_formativo", data["id_proyecto_formativo"]) is None:
            return "El proyecto formativo seleccionado no existe."
        coordinacion = get_entity("coordinacion", data["id_coordinacion"])
        if coordinacion is None:
            return "La coordinación seleccionada no existe."
        if data.get("id_instructor"):
            instructor = get_entity("instructor", data["id_instructor"])
            if instructor is None:
                return "El instructor seleccionado no existe."
            if not instructor.get("area_id") or instructor["area_id"] != programa["area_id"]:
                return "El instructor asignado debe pertenecer a la misma área del programa."
            centro_coordinacion = get_entity("centro", coordinacion["centro_id"])
            if centro_coordinacion is None or instructor["centro_id"] != centro_coordinacion["id"]:
                return "El instructor asignado debe pertenecer al centro de formación de la coordinación seleccionada."
    if entity == "fase_proyecto" and get_entity("proyecto_formativo", data["id_proyecto_formativo"]) is None:
        return "El proyecto formativo seleccionado no existe."
    if entity == "actividad_proyecto" and get_entity("fase_proyecto", data["id_fase_proyecto"]) is None:
        return "La fase seleccionada no existe."
    if entity == "actividad_aprendizaje" and get_entity("actividad_proyecto", data["id_actividad_proyecto"]) is None:
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
