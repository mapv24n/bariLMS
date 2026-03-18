import copy
import os
import sqlite3
from functools import wraps

from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "bari-lms-dev-key")
app.config["DATABASE"] = os.path.join(app.root_path, "bari_lms.db")

ROLE_TO_SLUG = {
    "Administrador": "administrador",
    "Administrativo": "administrativo",
    "Instructor": "instructor",
    "Aprendiz": "aprendiz",
}

AVAILABLE_ROLES = list(ROLE_TO_SLUG.keys())

DEFAULT_USERS = [
    {
        "email": "admin@senalearn.edu.co",
        "password": "Admin123*",
        "role": "Administrador",
        "name": "Laura Moreno",
        "active": 1,
    },
    {
        "email": "administrativo@senalearn.edu.co",
        "password": "Adminvo123*",
        "role": "Administrativo",
        "name": "Carlos Ruiz",
        "active": 1,
    },
    {
        "email": "instructor@senalearn.edu.co",
        "password": "Instructor123*",
        "role": "Instructor",
        "name": "Diana Beltran",
        "active": 1,
    },
    {
        "email": "aprendiz@senalearn.edu.co",
        "password": "Aprendiz123*",
        "role": "Aprendiz",
        "name": "Miguel Torres",
        "active": 1,
    },
]

DEFAULT_LEVELS = [
    "Técnico",
    "Tecnólogo",
    "Operario",
    "Auxiliar",
    "Curso",
]

DASHBOARDS = {
    "administrador": {
        "role": "Administrador",
        "icon": "fa-user-shield",
        "area": "Direccionamiento institucional",
        "title": "Tablero del Administrador",
        "text": "Supervisa la operación general de BARÍ LMS, define lineamientos y controla el acceso de los perfiles del LMS.",
        "footer": "BARÍ LMS SENA - Administrador",
        "menu_heading": "Administración",
        "menu": [
            {"icon": "fa-users-cog", "label": "Usuarios y roles", "endpoint": "admin_users"},
            {"icon": "fa-sitemap", "label": "Estructura institucional", "endpoint": "admin_structure"},
            {"icon": "fa-graduation-cap", "label": "Gestión académica", "endpoint": "admin_academic"},
            {
                "icon": "fa-chart-pie",
                "label": "Indicadores",
                "endpoint": "dashboard",
                "endpoint_kwargs": {"role_slug": "administrador"},
            },
        ],
        "metrics": [
            {"label": "Usuarios activos", "value": "0", "icon": "fa-users"},
            {"label": "Regionales", "value": "0", "icon": "fa-map-marked-alt"},
            {"label": "Roles configurados", "value": "0", "icon": "fa-user-shield"},
            {"label": "Centros", "value": "0", "icon": "fa-building"},
        ],
        "tasks_title": "Frentes prioritarios",
        "tasks": [
            {"title": "Gestión de usuarios", "text": "Aprobar nuevas cuentas y validar asignación de perfiles."},
            {"title": "Estructura institucional", "text": "Administrar regionales, centros, coordinaciones, sedes y ambientes."},
            {"title": "Seguimiento", "text": "Consultar indicadores de uso, permanencia y actividad por centro."},
        ],
        "table_title": "Resumen operativo",
        "table_headers": ["Unidad", "Estado", "Observación"],
        "table_rows": [
            ["Regional Distrito Capital", "98%", "Sin novedades"],
            ["Regional Antioquia", "94%", "Actualizar instructores"],
            ["Regional Valle", "91%", "Revisión de permisos"],
        ],
    },
    "administrativo": {
        "role": "Administrativo",
        "icon": "fa-clipboard-check",
        "area": "Apoyo académico y operativo",
        "title": "Tablero Administrativo",
        "text": "Consolida fichas, programas, ambientes y apoyo documental para el despliegue de la formación por proyectos.",
        "footer": "BARÍ LMS SENA - Administrativo",
        "menu_heading": "Operación",
        "menu": [
            {
                "icon": "fa-folder-open",
                "label": "Fichas y programas",
                "endpoint": "dashboard",
                "endpoint_kwargs": {"role_slug": "administrativo"},
            },
            {
                "icon": "fa-school",
                "label": "Ambientes y sedes",
                "endpoint": "dashboard",
                "endpoint_kwargs": {"role_slug": "administrativo"},
            },
        ],
        "metrics": [
            {"label": "Fichas activas", "value": "86", "icon": "fa-id-badge"},
            {"label": "Programas", "value": "27", "icon": "fa-graduation-cap"},
            {"label": "Ambientes", "value": "49", "icon": "fa-door-open"},
            {"label": "Solicitudes", "value": "12", "icon": "fa-clipboard-list"},
        ],
        "tasks_title": "Pendientes",
        "tasks": [
            {"title": "Matrícula", "text": "Consolidar aprendices por ficha y programa."},
            {"title": "Ambientes", "text": "Validar capacidad y disponibilidad por sede."},
            {"title": "Soporte documental", "text": "Publicar formatos y circulares internas."},
        ],
        "table_title": "Control académico",
        "table_headers": ["Ficha", "Programa", "Estado"],
        "table_rows": [
            ["ADSI 2675854", "Análisis y Desarrollo", "Completa"],
            ["SST 2675921", "Seguridad y Salud", "Pendiente soporte"],
            ["Cocina 2676018", "Técnico en Cocina", "Actualizada"],
        ],
    },
    "instructor": {
        "role": "Instructor",
        "icon": "fa-chalkboard-teacher",
        "area": "Ejecución formativa",
        "title": "Tablero del Instructor",
        "text": "Organiza resultados de aprendizaje, evidencias, proyectos y seguimiento del avance de cada ficha.",
        "footer": "BARÍ LMS SENA - Instructor",
        "menu_heading": "Formación",
        "menu": [
            {
                "icon": "fa-layer-group",
                "label": "Mis Fichas",
                "endpoint": "instructor_fichas",
            },
            {
                "icon": "fa-clipboard-check",
                "label": "Evaluación",
                "endpoint": "dashboard",
                "endpoint_kwargs": {"role_slug": "instructor"},
            },
            {
                "icon": "fa-key",
                "label": "Cambiar contraseña",
                "endpoint": "instructor_change_password",
            },
        ],
        "metrics": [
            {"label": "Fichas a cargo", "value": "6", "icon": "fa-layer-group"},
            {"label": "Proyectos activos", "value": "18", "icon": "fa-project-diagram"},
            {"label": "Evidencias por revisar", "value": "43", "icon": "fa-tasks"},
            {"label": "Alertas de asistencia", "value": "5", "icon": "fa-user-clock"},
        ],
        "tasks_title": "Acciones docentes",
        "tasks": [
            {"title": "Planeación", "text": "Programar actividades alineadas al proyecto formativo."},
            {"title": "Seguimiento", "text": "Retroalimentar evidencias y avances semanales."},
            {"title": "Evaluación", "text": "Registrar desempeño por resultado de aprendizaje."},
        ],
        "table_title": "Seguimiento de fichas",
        "table_headers": ["Ficha", "Actividad", "Estado"],
        "table_rows": [
            ["Ficha 2675854", "Sprint de prototipo", "15 entregas pendientes"],
            ["Ficha 2675860", "Sustentación parcial", "Programada"],
            ["Ficha 2675902", "Bitácora de proyecto", "Al día"],
        ],
    },
    "aprendiz": {
        "role": "Aprendiz",
        "icon": "fa-user-graduate",
        "area": "Ruta de aprendizaje",
        "title": "Tablero del Aprendiz",
        "text": "Consulta tu avance del proyecto, entregas, evidencias, horario y comunicados del proceso formativo.",
        "footer": "BARÍ LMS SENA - Aprendiz",
        "menu_heading": "Aprendizaje",
        "menu": [
            {
                "icon": "fa-project-diagram",
                "label": "Mi proyecto",
                "endpoint": "dashboard",
                "endpoint_kwargs": {"role_slug": "aprendiz"},
            },
            {
                "icon": "fa-file-alt",
                "label": "Evidencias",
                "endpoint": "dashboard",
                "endpoint_kwargs": {"role_slug": "aprendiz"},
            },
        ],
        "metrics": [
            {"label": "Avance general", "value": "72%", "icon": "fa-chart-line"},
            {"label": "Evidencias pendientes", "value": "4", "icon": "fa-file-upload"},
            {"label": "Resultados aprobados", "value": "11", "icon": "fa-check-circle"},
            {"label": "Mensajes nuevos", "value": "3", "icon": "fa-comments"},
        ],
        "tasks_title": "Ruta personal",
        "tasks": [
            {"title": "Proyecto formativo", "text": "Consultar entregables y fechas de corte."},
            {"title": "Ruta individual", "text": "Ver resultados alcanzados y faltantes."},
            {"title": "Comunicación", "text": "Revisar mensajes de instructor y coordinación."},
        ],
        "table_title": "Próximas entregas",
        "table_headers": ["Actividad", "Fecha", "Estado"],
        "table_rows": [
            ["Bitácora semanal", "14 de marzo de 2026", "Pendiente"],
            ["Prototipo funcional", "18 de marzo de 2026", "En progreso"],
            ["Autoevaluacion", "20 de marzo de 2026", "No iniciada"],
        ],
    },
}

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
        "parent_key": "coordinacion_id",
        "fields": ["id_coordinacion", "id_area", "documento", "nombres", "apellidos", "correo", "genero"],
        "required": ["id_coordinacion", "documento", "nombres", "apellidos"],
        "context_key": "coordinacion_id",
        "select_aliases": {
            "id_coordinacion": "coordinacion_id",
            "id_area": "area_id",
            "correo": "email",
            "id_usuario": "user_id",
        },
        "form_to_db": {"coordinacion_id": "id_coordinacion", "area_id": "id_area", "email": "correo"},
    },
    "aprendiz": {
        "table": "aprendiz",
        "label": "Aprendiz",
        "parent_key": "coordinacion_id",
        "fields": ["id_coordinacion", "documento", "nombres", "apellidos", "ficha"],
        "required": ["id_coordinacion", "documento", "nombres", "apellidos"],
        "context_key": "coordinacion_id",
        "select_aliases": {"id_coordinacion": "coordinacion_id"},
        "form_to_db": {"coordinacion_id": "id_coordinacion"},
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
}

TABLE_NAMES = {
    "usuario": "usuario",
    "regional": "regional",
    "centro": "centro",
    "coordinacion": "coordinacion",
    "sede": "sede",
    "instructor": "instructor",
    "aprendiz": "aprendiz",
    "ambiente": "ambiente",
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
        "email": "correo",
        "user_id": "id_usuario",
    },
    "aprendiz": {"coordinacion_id": "id_coordinacion"},
    "ambiente": {"sede_id": "id_sede"},
}


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def initialize_database():
    db = get_db()
    existing_tables = {
        row["name"]
        for row in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    }
    for old_name, new_name in LEGACY_TABLE_NAMES.items():
        if old_name in existing_tables and new_name not in existing_tables:
            db.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")
            existing_tables.remove(old_name)
            existing_tables.add(new_name)

    for table_name, rename_map in COLUMN_RENAMES.items():
        if table_name not in existing_tables:
            continue
        table_columns = {
            row["name"] for row in db.execute(f"PRAGMA table_info({table_name})").fetchall()
        }
        for old_column, new_column in rename_map.items():
            if old_column in table_columns and new_column not in table_columns:
                db.execute(f"ALTER TABLE {table_name} RENAME COLUMN {old_column} TO {new_column}")
                table_columns.remove(old_column)
                table_columns.add(new_column)

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            correo TEXT UNIQUE NOT NULL,
            contrasena_hash TEXT NOT NULL,
            rol TEXT NOT NULL,
            nombre TEXT NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1,
            creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS regional (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS centro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_regional INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_regional) REFERENCES regional(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS coordinacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_centro INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_centro) REFERENCES centro(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS sede (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_centro INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_centro) REFERENCES centro(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS instructor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_coordinacion INTEGER NOT NULL,
            documento TEXT NOT NULL,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            correo TEXT,
            id_usuario INTEGER,
            genero TEXT DEFAULT 'M',
            FOREIGN KEY (id_coordinacion) REFERENCES coordinacion(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS aprendiz (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_coordinacion INTEGER NOT NULL,
            documento TEXT NOT NULL,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            ficha TEXT,
            FOREIGN KEY (id_coordinacion) REFERENCES coordinacion(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS ambiente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_sede INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            capacidad INTEGER,
            FOREIGN KEY (id_sede) REFERENCES sede(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS red_conocimiento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS area (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_red_conocimiento INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_red_conocimiento) REFERENCES red_conocimiento(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS nivel_formacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS programa_formacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS proyecto_formativo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS fase_proyecto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_proyecto_formativo INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_proyecto_formativo) REFERENCES proyecto_formativo(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS actividad_proyecto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_fase_proyecto INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_fase_proyecto) REFERENCES fase_proyecto(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS actividad_aprendizaje (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_actividad_proyecto INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_actividad_proyecto) REFERENCES actividad_proyecto(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS guia_aprendizaje (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_actividad_aprendizaje INTEGER NOT NULL UNIQUE,
            url TEXT NOT NULL,
            subido_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_actividad_aprendizaje) REFERENCES actividad_aprendizaje(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS evidencia_aprendizaje (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_actividad_aprendizaje INTEGER NOT NULL,
            descripcion TEXT,
            creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_actividad_aprendizaje) REFERENCES actividad_aprendizaje(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS entrega_evidencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_evidencia_aprendizaje INTEGER NOT NULL,
            id_usuario INTEGER NOT NULL,
            url TEXT NOT NULL,
            calificacion REAL,
            observaciones TEXT,
            entregado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_evidencia_aprendizaje) REFERENCES evidencia_aprendizaje(id) ON DELETE CASCADE,
            FOREIGN KEY (id_usuario) REFERENCES usuario(id) ON DELETE CASCADE
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS ficha_instructor_competencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_ficha INTEGER NOT NULL,
            id_instructor INTEGER NOT NULL,
            UNIQUE(id_ficha, id_instructor),
            FOREIGN KEY (id_ficha) REFERENCES ficha_formacion(id) ON DELETE CASCADE,
            FOREIGN KEY (id_instructor) REFERENCES instructor(id) ON DELETE CASCADE
        )
        """
    )
    db.commit()

    instructor_columns = {
        row["name"] for row in db.execute("PRAGMA table_info(instructor)").fetchall()
    }
    if "id_usuario" not in instructor_columns:
        db.execute("ALTER TABLE instructor ADD COLUMN id_usuario INTEGER")
        db.commit()
        instructor_columns.add("id_usuario")
    if "id_area" not in instructor_columns:
        db.execute("ALTER TABLE instructor ADD COLUMN id_area INTEGER")
        db.commit()
        instructor_columns.add("id_area")
    if "genero" not in instructor_columns:
        db.execute("ALTER TABLE instructor ADD COLUMN genero TEXT DEFAULT 'M'")
        db.commit()

    ficha_columns = {
        row["name"] for row in db.execute("PRAGMA table_info(ficha_formacion)").fetchall()
    }
    if "id_proyecto_formativo" not in ficha_columns:
        db.execute("ALTER TABLE ficha_formacion ADD COLUMN id_proyecto_formativo INTEGER")
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


with app.app_context():
    initialize_database()


def parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def current_user():
    email = session.get("user_email")
    if not email:
        return None

    user = get_user_by_email(email)
    if user is None or user["active"] != 1:
        session.clear()
        return None

    return {
        "id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "name": user["name"],
        "active": user["active"],
        "dashboard_slug": ROLE_TO_SLUG[user["role"]],
    }


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        user = current_user()
        if user is None:
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


def role_required(expected_role):
    def decorator(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            user = current_user()
            if user is None:
                return redirect(url_for("login"))
            if user["role"] != expected_role:
                return redirect(url_for("dashboard", role_slug=user["dashboard_slug"]))
            return view(**kwargs)

        return wrapped_view

    return decorator


@app.context_processor
def inject_session_user():
    return {
        "session_user": current_user(),
        "session_user_email": session.get("user_email", ""),
    }


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


def generate_instructor_email(documento, email):
    clean_email = (email or "").strip().lower()
    if clean_email:
        return clean_email
    return f"instructor.{documento}@barilms.local"


def create_linked_instructor_user(instructor_id, data):
    login_email = generate_instructor_email(data["documento"], data.get("correo"))
    if get_user_by_email(login_email) is not None:
        raise ValueError("Ya existe un usuario con el correo que se intenta asignar al instructor.")

    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO usuario (correo, contrasena_hash, rol, nombre, activo)
        VALUES (?, ?, 'Instructor', ?, 1)
        """,
        (
            login_email,
            generate_password_hash(data["documento"]),
            f"{data['nombres']} {data['apellidos']}".strip(),
        ),
    )
    user_id = cursor.lastrowid
    db.execute(
        """
        UPDATE instructor
        SET correo = ?, id_usuario = ?
        WHERE id = ?
        """,
        (login_email, user_id, instructor_id),
    )
    db.commit()
    return user_id


def sync_instructor_user(instructor_id, data):
    instructor = get_entity("instructor", instructor_id)
    if instructor is None:
        return

    login_email = generate_instructor_email(data["documento"], data.get("correo"))
    db = get_db()

    if instructor["user_id"]:
        existing_user = get_user_by_email(login_email)
        if existing_user is not None and existing_user["id"] != instructor["user_id"]:
            raise ValueError("Ya existe un usuario con el correo que se intenta asignar al instructor.")

        db.execute(
            """
            UPDATE usuario
            SET correo = ?, contrasena_hash = ?, rol = 'Instructor', nombre = ?, activo = 1
            WHERE id = ?
            """,
            (
                login_email,
                generate_password_hash(data["documento"]),
                f"{data['nombres']} {data['apellidos']}".strip(),
                instructor["user_id"],
            ),
        )
        db.execute(
            """
            UPDATE instructor
            SET correo = ?
            WHERE id = ?
            """,
            (login_email, instructor_id),
        )
        db.commit()
        return

    create_linked_instructor_user(instructor_id, data)


def delete_linked_instructor_user(instructor_id):
    instructor = get_entity("instructor", instructor_id)
    if instructor is None or not instructor["user_id"]:
        return

    db = get_db()
    db.execute("DELETE FROM usuario WHERE id = ?", (instructor["user_id"],))
    db.commit()


def get_all_users():
    return get_db().execute(
        """
        SELECT id, correo AS email, rol AS role, nombre AS name, activo AS active, creado_en AS created_at
        FROM usuario
        ORDER BY creado_en DESC, id DESC
        """
    ).fetchall()


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
    total_active = db.execute("SELECT COUNT(*) AS total FROM usuario WHERE activo = 1").fetchone()["total"]
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
    config["table_rows"] = [[row["name"], row["role"], row["email"]] for row in latest_users] or [
        ["Sin registros", "-", "-"]
    ]
    return config


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
    if edit_entity in {"instructor", "aprendiz"} and (
        editing_item is None or editing_item["coordinacion_id"] != coordinacion_id
    ):
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
        "instructores": (
            get_entities("instructor", "id_coordinacion = ?", (coordinacion_id,), "nombres ASC, apellidos ASC")
            if coordinacion_id
            else []
        ),
        "aprendices": (
            get_entities("aprendiz", "id_coordinacion = ?", (coordinacion_id,), "nombres ASC, apellidos ASC")
            if coordinacion_id
            else []
        ),
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
    overrides = overrides or {}
    args.update(overrides)
    return {key: value for key, value in args.items() if value}


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
    if entity == "instructor" and data.get("id_area") is not None and get_entity("area", data["id_area"]) is None:
        return "El área académica seleccionada no existe."
    if entity == "ficha" and data["id_instructor"] in ("", None):
        data["id_instructor"] = None

    return None


def insert_entity(entity, data):
    config = ENTITY_CONFIG[entity]
    columns = ", ".join(config["fields"])
    placeholders = ", ".join(["?"] * len(config["fields"]))
    values = tuple(data[field] for field in config["fields"])
    db = get_db()
    cursor = db.execute(
        f"INSERT INTO {config['table']} ({columns}) VALUES ({placeholders})",
        values,
    )
    db.commit()
    return cursor.lastrowid


def update_entity(entity, item_id, data):
    config = ENTITY_CONFIG[entity]
    assignments = ", ".join([f"{field} = ?" for field in config["fields"]])
    values = tuple(data[field] for field in config["fields"]) + (item_id,)
    db = get_db()
    db.execute(
        f"UPDATE {config['table']} SET {assignments} WHERE id = ?",
        values,
    )
    db.commit()


def delete_entity(entity, item_id):
    db = get_db()
    db.execute(f"DELETE FROM {ENTITY_CONFIG[entity]['table']} WHERE id = ?", (item_id,))
    db.commit()


def entity_select_clause(entity):
    config = ENTITY_CONFIG[entity]
    alias_map = config.get("select_aliases", {})
    fields = ["id"]
    for field in config["fields"]:
        alias = alias_map.get(field)
        fields.append(f"{field} AS {alias}" if alias else field)
    if entity == "instructor" and "id_usuario AS user_id" not in fields and "user_id" not in alias_map.values():
        fields.append("id_usuario AS user_id")
    if entity == "instructor" and "id_area AS area_id" not in fields:
        fields.append("id_area AS area_id")
    return ", ".join(fields)


@app.route("/")
def home():
    user = current_user()
    if user:
        return redirect(url_for("dashboard", role_slug=user["dashboard_slug"]))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "")
        user = get_user_by_email(email)

        if (
            user is None
            or user["active"] != 1
            or user["role"] != role
            or not check_password_hash(user["password_hash"], password)
        ):
            flash("Credenciales o perfil incorrectos. Usa uno de los accesos demo listados.", "danger")
            return render_template("login.html", demo_users=DEFAULT_USERS)

        session.clear()
        session["user_email"] = user["email"]
        return redirect(url_for("dashboard", role_slug=ROLE_TO_SLUG[user["role"]]))

    if current_user():
        return redirect(url_for("home"))

    return render_template("login.html", demo_users=DEFAULT_USERS)


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard/<role_slug>")
@login_required
def dashboard(role_slug):
    user = current_user()
    config = DASHBOARDS.get(role_slug)

    if config is None:
        return redirect(url_for("home"))

    if user["dashboard_slug"] != role_slug:
        return redirect(url_for("dashboard", role_slug=user["dashboard_slug"]))

    if role_slug == "administrador":
        config = get_admin_dashboard_data()

    return render_template("dashboard.html", dashboard=config, user=user)


@app.route("/admin/users")
@role_required("Administrador")
def admin_users():
    return render_template(
        "admin_users.html",
        user=current_user(),
        users=get_all_users(),
        roles=AVAILABLE_ROLES,
        form_data={},
        editing_user=None,
    )


@app.post("/admin/users/create")
@role_required("Administrador")
def admin_users_create():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    role = request.form.get("role", "").strip()
    password = request.form.get("password", "")
    active = 1 if request.form.get("active") == "on" else 0

    form_data = {"name": name, "email": email, "role": role, "active": active}

    if not name or not email or not role or not password:
        flash("Todos los campos son obligatorios para crear el usuario.", "danger")
        return render_template(
            "admin_users.html",
            user=current_user(),
            users=get_all_users(),
            roles=AVAILABLE_ROLES,
            form_data=form_data,
            editing_user=None,
        )

    if role not in AVAILABLE_ROLES:
        flash("El rol seleccionado no es válido.", "danger")
        return redirect(url_for("admin_users"))

    if get_user_by_email(email) is not None:
        flash("Ya existe un usuario registrado con ese correo.", "danger")
        return render_template(
            "admin_users.html",
            user=current_user(),
            users=get_all_users(),
            roles=AVAILABLE_ROLES,
            form_data=form_data,
            editing_user=None,
        )

    db = get_db()
    db.execute(
        """
        INSERT INTO usuario (correo, contrasena_hash, rol, nombre, activo)
        VALUES (?, ?, ?, ?, ?)
        """,
        (email, generate_password_hash(password), role, name, active),
    )
    db.commit()
    flash("Usuario creado correctamente.", "success")
    return redirect(url_for("admin_users"))


@app.get("/admin/users/<int:user_id>/edit")
@role_required("Administrador")
def admin_users_edit(user_id):
    editing_user = get_user_by_id(user_id)
    if editing_user is None:
        flash("El usuario solicitado no existe.", "danger")
        return redirect(url_for("admin_users"))

    return render_template(
        "admin_users.html",
        user=current_user(),
        users=get_all_users(),
        roles=AVAILABLE_ROLES,
        form_data={
            "name": editing_user["name"],
            "email": editing_user["email"],
            "role": editing_user["role"],
            "active": editing_user["active"],
        },
        editing_user=editing_user,
    )


@app.post("/admin/users/<int:user_id>/update")
@role_required("Administrador")
def admin_users_update(user_id):
    editing_user = get_user_by_id(user_id)
    if editing_user is None:
        flash("El usuario solicitado no existe.", "danger")
        return redirect(url_for("admin_users"))

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    role = request.form.get("role", "").strip()
    password = request.form.get("password", "")
    active = 1 if request.form.get("active") == "on" else 0

    if not name or not email or not role:
        flash("Nombre, correo y rol son obligatorios.", "danger")
        return redirect(url_for("admin_users_edit", user_id=user_id))

    if role not in AVAILABLE_ROLES:
        flash("El rol seleccionado no es válido.", "danger")
        return redirect(url_for("admin_users_edit", user_id=user_id))

    existing = get_user_by_email(email)
    if existing is not None and existing["id"] != user_id:
        flash("Ya existe otro usuario con ese correo.", "danger")
        return redirect(url_for("admin_users_edit", user_id=user_id))

    if current_user()["id"] == user_id and active != 1:
        flash("No puedes desactivar tu propia cuenta mientras la estas usando.", "danger")
        return redirect(url_for("admin_users_edit", user_id=user_id))

    db = get_db()
    if password:
        db.execute(
            """
            UPDATE usuario
            SET nombre = ?, correo = ?, rol = ?, activo = ?, contrasena_hash = ?
            WHERE id = ?
            """,
            (name, email, role, active, generate_password_hash(password), user_id),
        )
    else:
        db.execute(
            """
            UPDATE usuario
            SET nombre = ?, correo = ?, rol = ?, activo = ?
            WHERE id = ?
            """,
            (name, email, role, active, user_id),
        )
    db.commit()

    if current_user()["id"] == user_id:
        session["user_email"] = email

    flash("Usuario actualizado correctamente.", "success")
    return redirect(url_for("admin_users"))


@app.post("/admin/users/<int:user_id>/delete")
@role_required("Administrador")
def admin_users_delete(user_id):
    target_user = get_user_by_id(user_id)
    if target_user is None:
        flash("El usuario solicitado no existe.", "danger")
        return redirect(url_for("admin_users"))

    if current_user()["id"] == user_id:
        flash("No puedes eliminar tu propia cuenta.", "danger")
        return redirect(url_for("admin_users"))

    db = get_db()
    db.execute("DELETE FROM usuario WHERE id = ?", (user_id,))
    db.commit()
    flash("Usuario eliminado correctamente.", "success")
    return redirect(url_for("admin_users"))


@app.route("/admin/structure")
@role_required("Administrador")
def admin_structure():
    context = normalize_structure_context(request.args)
    return render_template("admin_structure.html", user=current_user(), **context)


@app.post("/admin/structure/<entity>/create")
@role_required("Administrador")
def admin_structure_create(entity):
    if entity not in ENTITY_CONFIG:
        return redirect(url_for("admin_structure"))

    data = entity_form_data(entity, request.form)
    validation_error = validate_entity_payload(entity, data)
    if validation_error:
        flash(validation_error, "danger")
        return redirect(url_for("admin_structure", **structure_redirect_args(request.form)))

    created_id = None
    try:
        created_id = insert_entity(entity, data)
        if entity == "instructor":
            create_linked_instructor_user(created_id, data)
    except sqlite3.IntegrityError:
        flash(f"No fue posible crear {ENTITY_CONFIG[entity]['label'].lower()}. Verifica que no exista un dato duplicado.", "danger")
        return redirect(url_for("admin_structure", **structure_redirect_args(request.form)))
    except ValueError as error:
        if entity == "instructor" and created_id is not None:
            delete_entity("instructor", created_id)
        flash(str(error), "danger")
        return redirect(url_for("admin_structure", **structure_redirect_args(request.form)))
    redirect_args = structure_redirect_args(
        request.form,
        {ENTITY_CONFIG[entity]["context_key"]: created_id, "edit_entity": None, "edit_id": None},
    )
    flash(f"{ENTITY_CONFIG[entity]['label']} creada correctamente.", "success")
    return redirect(url_for("admin_structure", **redirect_args))


@app.get("/admin/structure/<entity>/<int:item_id>/edit")
@role_required("Administrador")
def admin_structure_edit(entity, item_id):
    if entity not in ENTITY_CONFIG:
        return redirect(url_for("admin_structure"))

    item = get_entity(entity, item_id)
    if item is None:
        flash("El elemento solicitado no existe.", "danger")
        return redirect(url_for("admin_structure"))

    overrides = {"edit_entity": entity, "edit_id": item_id}
    if entity == "regional":
        overrides["regional_id"] = item_id
    elif entity == "centro":
        overrides["regional_id"] = item["regional_id"]
        overrides["centro_id"] = item_id
    elif entity in {"coordinacion", "sede"}:
        centro = get_entity("centro", item["centro_id"])
        overrides["regional_id"] = centro["regional_id"]
        overrides["centro_id"] = item["centro_id"]
        overrides[ENTITY_CONFIG[entity]["context_key"]] = item_id
    elif entity in {"instructor", "aprendiz"}:
        coordinacion = get_entity("coordinacion", item["coordinacion_id"])
        centro = get_entity("centro", coordinacion["centro_id"])
        overrides["regional_id"] = centro["regional_id"]
        overrides["centro_id"] = centro["id"]
        overrides["coordinacion_id"] = coordinacion["id"]
    elif entity == "ambiente":
        sede = get_entity("sede", item["sede_id"])
        centro = get_entity("centro", sede["centro_id"])
        overrides["regional_id"] = centro["regional_id"]
        overrides["centro_id"] = centro["id"]
        overrides["sede_id"] = sede["id"]

    return redirect(url_for("admin_structure", **overrides))


@app.post("/admin/structure/<entity>/<int:item_id>/update")
@role_required("Administrador")
def admin_structure_update(entity, item_id):
    if entity not in ENTITY_CONFIG:
        return redirect(url_for("admin_structure"))

    existing = get_entity(entity, item_id)
    if existing is None:
        flash("El elemento solicitado no existe.", "danger")
        return redirect(url_for("admin_structure"))

    data = entity_form_data(entity, request.form)
    validation_error = validate_entity_payload(entity, data)
    if validation_error:
        flash(validation_error, "danger")
        redirect_args = structure_redirect_args(
            request.form,
            {"edit_entity": entity, "edit_id": item_id},
        )
        return redirect(url_for("admin_structure", **redirect_args))

    try:
        update_entity(entity, item_id, data)
        if entity == "instructor":
            sync_instructor_user(item_id, data)
    except sqlite3.IntegrityError:
        flash(f"No fue posible actualizar {ENTITY_CONFIG[entity]['label'].lower()}. Verifica los datos ingresados.", "danger")
        redirect_args = structure_redirect_args(
            request.form,
            {"edit_entity": entity, "edit_id": item_id},
        )
        return redirect(url_for("admin_structure", **redirect_args))
    except ValueError as error:
        flash(str(error), "danger")
        redirect_args = structure_redirect_args(
            request.form,
            {"edit_entity": entity, "edit_id": item_id},
        )
        return redirect(url_for("admin_structure", **redirect_args))
    flash(f"{ENTITY_CONFIG[entity]['label']} actualizada correctamente.", "success")
    redirect_args = structure_redirect_args(request.form, {"edit_entity": None, "edit_id": None})
    return redirect(url_for("admin_structure", **redirect_args))


@app.post("/admin/structure/<entity>/<int:item_id>/delete")
@role_required("Administrador")
def admin_structure_delete(entity, item_id):
    if entity not in ENTITY_CONFIG:
        return redirect(url_for("admin_structure"))

    item = get_entity(entity, item_id)
    if item is None:
        flash("El elemento solicitado no existe.", "danger")
        return redirect(url_for("admin_structure"))

    redirect_args = structure_redirect_args(request.form)
    if entity == "regional" and redirect_args.get("regional_id") == item_id:
        redirect_args.pop("regional_id", None)
        redirect_args.pop("centro_id", None)
        redirect_args.pop("coordinacion_id", None)
        redirect_args.pop("sede_id", None)
    elif entity == "centro" and redirect_args.get("centro_id") == item_id:
        redirect_args.pop("centro_id", None)
        redirect_args.pop("coordinacion_id", None)
        redirect_args.pop("sede_id", None)
    elif entity == "coordinacion" and redirect_args.get("coordinacion_id") == item_id:
        redirect_args.pop("coordinacion_id", None)
    elif entity == "sede" and redirect_args.get("sede_id") == item_id:
        redirect_args.pop("sede_id", None)

    if entity == "instructor":
        delete_linked_instructor_user(item_id)
    delete_entity(entity, item_id)
    flash(f"{ENTITY_CONFIG[entity]['label']} eliminada correctamente.", "success")
    return redirect(url_for("admin_structure", **redirect_args))


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
    overrides = overrides or {}
    args.update(overrides)
    return {key: value for key, value in args.items() if value}


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
        proyecto_formativo = get_entity("proyecto_formativo", data["id_proyecto_formativo"])
        if proyecto_formativo is None:
            return "El proyecto formativo seleccionado no existe."
        coordinacion = get_entity("coordinacion", data["id_coordinacion"])
        if coordinacion is None:
            return "La coordinación seleccionada no existe."
        if data.get("id_instructor"):
            instructor = get_entity("instructor", data["id_instructor"])
            if instructor is None:
                return "El instructor seleccionado no existe."
            instructor_area_id = instructor["area_id"] if "area_id" in instructor.keys() else None
            if not instructor_area_id or instructor_area_id != programa["area_id"]:
                return "El instructor asignado debe pertenecer a la misma área del programa."
            if instructor["coordinacion_id"] != data["id_coordinacion"]:
                return "El instructor asignado debe pertenecer a la coordinación seleccionada."
    if entity == "fase_proyecto":
        if get_entity("proyecto_formativo", data["id_proyecto_formativo"]) is None:
            return "El proyecto formativo seleccionado no existe."
    if entity == "actividad_proyecto":
        if get_entity("fase_proyecto", data["id_fase_proyecto"]) is None:
            return "La fase seleccionada no existe."
    if entity == "actividad_aprendizaje":
        if get_entity("actividad_proyecto", data["id_actividad_proyecto"]) is None:
            return "La actividad de proyecto seleccionada no existe."

    return None


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
    if fase_proyecto is None or (
        proyecto_formativo_id and fase_proyecto["proyecto_formativo_id"] != proyecto_formativo_id
    ):
        fase_proyecto = None
        fase_id = None
        actividad_proyecto_id = None

    actividad_proyecto = get_entity("actividad_proyecto", actividad_proyecto_id)
    if actividad_proyecto is None or (fase_id and actividad_proyecto["fase_id"] != fase_id):
        actividad_proyecto = None
        actividad_proyecto_id = None

    if edit_entity not in {
        "red",
        "area",
        "nivel",
        "programa",
        "ficha",
        "proyecto_formativo",
        "fase_proyecto",
        "actividad_proyecto",
        "actividad_aprendizaje",
    }:
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
    if edit_entity == "fase_proyecto" and (
        editing_item is None or editing_item["proyecto_formativo_id"] != proyecto_formativo_id
    ):
        edit_entity = None
        edit_id = None
    if edit_entity == "actividad_proyecto" and (editing_item is None or editing_item["fase_id"] != fase_id):
        edit_entity = None
        edit_id = None
    if edit_entity == "actividad_aprendizaje" and (
        editing_item is None or editing_item["actividad_proyecto_id"] != actividad_proyecto_id
    ):
        edit_entity = None
        edit_id = None
    if edit_entity in {"red", "nivel"} and editing_item is None:
        edit_entity = None
        edit_id = None
    if edit_entity == "proyecto_formativo" and editing_item is None:
        edit_entity = None
        edit_id = None

    fichas = []
    if programa_id:
        db = get_db()
        fichas = db.execute(
            """
            SELECT f.id, f.numero, f.id_programa_formacion AS programa_id,
                   f.id_proyecto_formativo AS proyecto_formativo_id,
                   f.id_coordinacion AS coordinacion_id, f.id_instructor AS instructor_id,
                   pf.nombre AS proyecto_formativo_nombre,
                   c.nombre AS coordinacion_nombre,
                   i.nombres || ' ' || i.apellidos AS instructor_nombre,
                   i.genero AS instructor_genero
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
                   id_area AS area_id, id_coordinacion AS coordinacion_id,
                   genero
            FROM instructor
            WHERE id_area = ?
            ORDER BY nombres ASC, apellidos ASC
            """,
            (programa["area_id"],),
        ).fetchall()

    # Instructores a competencias de la ficha que se está editando
    instructores_competencia_ficha = []
    if edit_entity == "ficha" and edit_id:
        instructores_competencia_ficha = get_db().execute(
            """
            SELECT ic.id_instructor AS id,
                   i.nombres, i.apellidos, i.genero,
                   i.id_area AS area_id, i.id_coordinacion AS coordinacion_id
            FROM ficha_instructor_competencia ic
            JOIN instructor i ON i.id = ic.id_instructor
            WHERE ic.id_ficha = ?
            ORDER BY i.nombres ASC, i.apellidos ASC
            """,
            (edit_id,),
        ).fetchall()

    fases_proyecto = (
        get_entities("fase_proyecto", "id_proyecto_formativo = ?", (proyecto_formativo_id,), "nombre ASC")
        if proyecto_formativo_id
        else []
    )
    actividades_proyecto = (
        get_entities("actividad_proyecto", "id_fase_proyecto = ?", (fase_id,), "nombre ASC")
        if fase_id
        else []
    )
    actividades_aprendizaje = (
        get_entities("actividad_aprendizaje", "id_actividad_proyecto = ?", (actividad_proyecto_id,), "nombre ASC")
        if actividad_proyecto_id
        else []
    )

    return {
        "redes": get_entities("red", order_by="nombre ASC"),
        "areas": get_entities("area", "id_red_conocimiento = ?", (red_id,), "nombre ASC") if red_id else [],
        "niveles": get_entities("nivel", order_by="nombre ASC"),
        "programas": get_entities("programa", "id_area = ?", (area_id,), "nombre ASC") if area_id else [],
        "fichas": fichas,
        "coordinaciones_disponibles": get_entities("coordinacion", order_by="nombre ASC"),
        "instructores_area": instructores_area,
        "instructores_competencia_ficha": instructores_competencia_ficha,
        "proyectos_formativos": get_entities("proyecto_formativo", order_by="codigo ASC, nombre ASC"),
        "fases_proyecto": fases_proyecto,
        "actividades_proyecto": actividades_proyecto,
        "actividades_aprendizaje": actividades_aprendizaje,
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


@app.route("/admin/academic")
@role_required("Administrador")
def admin_academic():
    context = normalize_academic_context(request.args)
    return render_template("admin_academic.html", user=current_user(), **context)


@app.post("/admin/academic/<entity>/create")
@role_required("Administrador")
def admin_academic_create(entity):
    if entity not in {"red", "area", "nivel", "programa", "ficha", "proyecto_formativo", "fase_proyecto", "actividad_proyecto", "actividad_aprendizaje"}:
        return redirect(url_for("admin_academic"))

    data = entity_form_data(entity, request.form)
    validation_error = validate_academic_payload(entity, data)
    if validation_error:
        flash(validation_error, "danger")
        return redirect(url_for("admin_academic", **academic_redirect_args(request.form)))

    try:
        created_id = insert_entity(entity, data)
    except sqlite3.IntegrityError:
        flash(f"No fue posible crear {ENTITY_CONFIG[entity]['label'].lower()}. Verifica que no exista un dato duplicado.", "danger")
        return redirect(url_for("admin_academic", **academic_redirect_args(request.form)))

    redirect_args = academic_redirect_args(
        request.form,
        {ENTITY_CONFIG[entity]["context_key"]: created_id, "edit_entity": None, "edit_id": None},
    )
    flash(f"{ENTITY_CONFIG[entity]['label']} creada correctamente.", "success")
    return redirect(url_for("admin_academic", **redirect_args))


@app.get("/admin/academic/<entity>/<int:item_id>/edit")
@role_required("Administrador")
def admin_academic_edit(entity, item_id):
    if entity not in {"red", "area", "nivel", "programa", "ficha", "proyecto_formativo", "fase_proyecto", "actividad_proyecto", "actividad_aprendizaje"}:
        return redirect(url_for("admin_academic"))

    item = get_entity(entity, item_id)
    if item is None:
        flash("El elemento solicitado no existe.", "danger")
        return redirect(url_for("admin_academic"))

    overrides = {"edit_entity": entity, "edit_id": item_id}
    if entity == "red":
        overrides["red_id"] = item_id
    elif entity == "area":
        overrides["red_id"] = item["red_id"]
        overrides["area_id"] = item_id
    elif entity == "programa":
        area = get_entity("area", item["area_id"])
        overrides["red_id"] = area["red_id"]
        overrides["area_id"] = item["area_id"]
        overrides["programa_id"] = item_id
        overrides["nivel_id"] = item["nivel_id"]
    elif entity == "ficha":
        programa = get_entity("programa", item["programa_id"])
        area = get_entity("area", programa["area_id"])
        overrides["red_id"] = area["red_id"]
        overrides["area_id"] = area["id"]
        overrides["programa_id"] = programa["id"]
    elif entity == "nivel":
        overrides["nivel_id"] = item_id
    elif entity == "proyecto_formativo":
        overrides["proyecto_formativo_id"] = item_id
    elif entity == "fase_proyecto":
        overrides["proyecto_formativo_id"] = item["proyecto_formativo_id"]
        overrides["fase_id"] = item_id
    elif entity == "actividad_proyecto":
        fase = get_entity("fase_proyecto", item["fase_id"])
        overrides["proyecto_formativo_id"] = fase["proyecto_formativo_id"]
        overrides["fase_id"] = fase["id"]
        overrides["actividad_proyecto_id"] = item_id
    elif entity == "actividad_aprendizaje":
        actividad_proyecto = get_entity("actividad_proyecto", item["actividad_proyecto_id"])
        fase = get_entity("fase_proyecto", actividad_proyecto["fase_id"])
        overrides["proyecto_formativo_id"] = fase["proyecto_formativo_id"]
        overrides["fase_id"] = fase["id"]
        overrides["actividad_proyecto_id"] = actividad_proyecto["id"]

    return redirect(url_for("admin_academic", **overrides))


@app.post("/admin/academic/<entity>/<int:item_id>/update")
@role_required("Administrador")
def admin_academic_update(entity, item_id):
    if entity not in {"red", "area", "nivel", "programa", "ficha", "proyecto_formativo", "fase_proyecto", "actividad_proyecto", "actividad_aprendizaje"}:
        return redirect(url_for("admin_academic"))

    existing = get_entity(entity, item_id)
    if existing is None:
        flash("El elemento solicitado no existe.", "danger")
        return redirect(url_for("admin_academic"))

    data = entity_form_data(entity, request.form)
    validation_error = validate_academic_payload(entity, data)
    if validation_error:
        flash(validation_error, "danger")
        return redirect(
            url_for(
                "admin_academic",
                **academic_redirect_args(request.form, {"edit_entity": entity, "edit_id": item_id}),
            )
        )

    try:
        update_entity(entity, item_id, data)
    except sqlite3.IntegrityError:
        flash(f"No fue posible actualizar {ENTITY_CONFIG[entity]['label'].lower()}. Verifica los datos ingresados.", "danger")
        return redirect(
            url_for(
                "admin_academic",
                **academic_redirect_args(request.form, {"edit_entity": entity, "edit_id": item_id}),
            )
        )

    flash(f"{ENTITY_CONFIG[entity]['label']} actualizada correctamente.", "success")
    return redirect(url_for("admin_academic", **academic_redirect_args(request.form)))


@app.post("/admin/academic/<entity>/<int:item_id>/delete")
@role_required("Administrador")
def admin_academic_delete(entity, item_id):
    if entity not in {"red", "area", "nivel", "programa", "ficha", "proyecto_formativo", "fase_proyecto", "actividad_proyecto", "actividad_aprendizaje"}:
        return redirect(url_for("admin_academic"))

    item = get_entity(entity, item_id)
    if item is None:
        flash("El elemento solicitado no existe.", "danger")
        return redirect(url_for("admin_academic"))

    redirect_args = academic_redirect_args(request.form)
    if entity == "red" and redirect_args.get("red_id") == item_id:
        redirect_args.pop("red_id", None)
        redirect_args.pop("area_id", None)
        redirect_args.pop("programa_id", None)
    elif entity == "area" and redirect_args.get("area_id") == item_id:
        redirect_args.pop("area_id", None)
        redirect_args.pop("programa_id", None)
    elif entity == "programa" and redirect_args.get("programa_id") == item_id:
        redirect_args.pop("programa_id", None)
    elif entity == "nivel" and redirect_args.get("nivel_id") == item_id:
        redirect_args.pop("nivel_id", None)
    elif entity == "proyecto_formativo" and redirect_args.get("proyecto_formativo_id") == item_id:
        redirect_args.pop("proyecto_formativo_id", None)
        redirect_args.pop("fase_id", None)
    elif entity == "fase_proyecto" and redirect_args.get("fase_id") == item_id:
        redirect_args.pop("fase_id", None)
        redirect_args.pop("actividad_proyecto_id", None)
    elif entity == "actividad_proyecto" and redirect_args.get("actividad_proyecto_id") == item_id:
        redirect_args.pop("actividad_proyecto_id", None)

    delete_entity(entity, item_id)
    flash(f"{ENTITY_CONFIG[entity]['label']} eliminada correctamente.", "success")
    return redirect(url_for("admin_academic", **redirect_args))


@app.post("/admin/academic/ficha/<int:ficha_id>/competencia/add")
@role_required("Administrador")
def admin_ficha_competencia_add(ficha_id):
    instructor_id = parse_int(request.form.get("instructor_id"))
    redirect_args = academic_redirect_args(
        request.form, {"edit_entity": "ficha", "edit_id": ficha_id}
    )
    if instructor_id is None:
        flash("Selecciona un instructor válido.", "danger")
        return redirect(url_for("admin_academic", **redirect_args))
    db = get_db()
    try:
        db.execute(
            "INSERT INTO ficha_instructor_competencia (id_ficha, id_instructor) VALUES (?, ?)",
            (ficha_id, instructor_id),
        )
        db.commit()
        flash("Instructor/a a competencias agregado correctamente.", "success")
    except sqlite3.IntegrityError:
        flash("Ese instructor/a ya está asignado/a a esta ficha.", "warning")
    return redirect(url_for("admin_academic", **redirect_args))


@app.post("/admin/academic/ficha/<int:ficha_id>/competencia/<int:instructor_id>/remove")
@role_required("Administrador")
def admin_ficha_competencia_remove(ficha_id, instructor_id):
    redirect_args = academic_redirect_args(
        request.form, {"edit_entity": "ficha", "edit_id": ficha_id}
    )
    db = get_db()
    db.execute(
        "DELETE FROM ficha_instructor_competencia WHERE id_ficha = ? AND id_instructor = ?",
        (ficha_id, instructor_id),
    )
    db.commit()
    flash("Instructor/a removido/a de competencias.", "success")
    return redirect(url_for("admin_academic", **redirect_args))


@app.route("/instructor/password", methods=["GET", "POST"])
@role_required("Instructor")
def instructor_change_password():
    user = current_user()

    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        user_record = get_user_by_email(user["email"])
        if user_record is None:
            flash("No fue posible validar el usuario actual.", "danger")
            return redirect(url_for("instructor_change_password"))

        if not current_password or not new_password or not confirm_password:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template("instructor/change_password.html", user=user)

        if not check_password_hash(user_record["password_hash"], current_password):
            flash("La contraseña actual es incorrecta.", "danger")
            return render_template("instructor/change_password.html", user=user)

        if new_password != confirm_password:
            flash("La nueva contraseña y su confirmación no coinciden.", "danger")
            return render_template("instructor/change_password.html", user=user)

        if len(new_password) < 8:
            flash("La nueva contraseña debe tener al menos 8 caracteres.", "danger")
            return render_template("instructor/change_password.html", user=user)

        if current_password == new_password:
            flash("La nueva contraseña debe ser diferente a la actual.", "danger")
            return render_template("instructor/change_password.html", user=user)

        db = get_db()
        db.execute(
            "UPDATE usuario SET contrasena_hash = ? WHERE id = ?",
            (generate_password_hash(new_password), user["id"]),
        )
        db.commit()
        flash("Contraseña actualizada correctamente.", "success")
        return redirect(url_for("instructor_change_password"))

    return render_template("instructor/change_password.html", user=user)


@app.route("/instructor/fichas")
@role_required("Instructor")
def instructor_fichas():
    user = current_user()
    db = get_db()
    instructor = db.execute(
        "SELECT id FROM instructor WHERE id_usuario = ?", (user["id"],)
    ).fetchone()

    fichas = []
    if instructor:
        fichas = db.execute(
            """
            SELECT f.id, f.numero,
                   p.nombre AS programa_nombre,
                   pf.nombre AS proyecto_nombre,
                   pf.codigo AS proyecto_codigo,
                   n.nombre AS nivel_nombre
            FROM ficha_formacion f
            JOIN programa_formacion p ON p.id = f.id_programa_formacion
            LEFT JOIN proyecto_formativo pf ON pf.id = f.id_proyecto_formativo
            LEFT JOIN nivel_formacion n ON n.id = p.id_nivel_formacion
            WHERE f.id_instructor = ?
            ORDER BY f.numero ASC
            """,
            (instructor["id"],),
        ).fetchall()

    return render_template("instructor/fichas.html", user=user, fichas=fichas)


@app.route("/instructor/ficha/<int:ficha_id>/fases")
@role_required("Instructor")
def instructor_fases(ficha_id):
    user = current_user()
    db = get_db()
    instructor = db.execute(
        "SELECT id FROM instructor WHERE id_usuario = ?", (user["id"],)
    ).fetchone()

    ficha = db.execute(
        """
        SELECT f.id, f.numero,
               p.nombre AS programa_nombre,
               pf.nombre AS proyecto_nombre,
               pf.codigo AS proyecto_codigo,
               pf.id AS proyecto_id,
               n.nombre AS nivel_nombre
        FROM ficha_formacion f
        JOIN programa_formacion p ON p.id = f.id_programa_formacion
        LEFT JOIN proyecto_formativo pf ON pf.id = f.id_proyecto_formativo
        LEFT JOIN nivel_formacion n ON n.id = p.id_nivel_formacion
        WHERE f.id = ?
        """,
        (ficha_id,),
    ).fetchone()

    if ficha is None:
        flash("La ficha solicitada no existe.", "danger")
        return redirect(url_for("instructor_fichas"))

    if instructor is None or db.execute(
        "SELECT id FROM ficha_formacion WHERE id = ? AND id_instructor = ?",
        (ficha_id, instructor["id"]),
    ).fetchone() is None:
        flash("No tienes acceso a esta ficha.", "danger")
        return redirect(url_for("instructor_fichas"))

    return render_template("instructor/fases.html", user=user, ficha=ficha)


@app.route("/api/instructor/ficha/<int:ficha_id>/tree")
@role_required("Instructor")
def api_instructor_ficha_tree(ficha_id):
    db = get_db()
    ficha = db.execute(
        "SELECT id_proyecto_formativo FROM ficha_formacion WHERE id = ?", (ficha_id,)
    ).fetchone()

    if ficha is None or ficha["id_proyecto_formativo"] is None:
        return jsonify({"fases": []})

    proyecto_id = ficha["id_proyecto_formativo"]
    fases = db.execute(
        "SELECT id, nombre FROM fase_proyecto WHERE id_proyecto_formativo = ? ORDER BY id ASC",
        (proyecto_id,),
    ).fetchall()

    result = []
    for fase in fases:
        acts_proy = db.execute(
            "SELECT id, nombre FROM actividad_proyecto WHERE id_fase_proyecto = ? ORDER BY id ASC",
            (fase["id"],),
        ).fetchall()

        fase_data = {"id": fase["id"], "nombre": fase["nombre"], "actividades_proyecto": []}
        for ap in acts_proy:
            acts_apr = db.execute(
                """
                SELECT aa.id, aa.nombre,
                       ga.url AS guia_url,
                       ea.id AS evidencia_id
                FROM actividad_aprendizaje aa
                LEFT JOIN guia_aprendizaje ga ON ga.id_actividad_aprendizaje = aa.id
                LEFT JOIN evidencia_aprendizaje ea ON ea.id_actividad_aprendizaje = aa.id
                WHERE aa.id_actividad_proyecto = ?
                ORDER BY aa.id ASC
                """,
                (ap["id"],),
            ).fetchall()

            ap_data = {
                "id": ap["id"],
                "nombre": ap["nombre"],
                "actividades_aprendizaje": [
                    {
                        "id": aa["id"],
                        "nombre": aa["nombre"],
                        "guia_url": aa["guia_url"],
                        "evidencia_id": aa["evidencia_id"],
                    }
                    for aa in acts_apr
                ],
            }
            fase_data["actividades_proyecto"].append(ap_data)
        result.append(fase_data)

    return jsonify({"fases": result})


@app.post("/api/instructor/actividad/<int:act_id>/guia")
@role_required("Instructor")
def api_instructor_guia_save(act_id):
    data = request.get_json() or {}
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"ok": False, "error": "URL requerida"}), 400

    db = get_db()
    existing = db.execute(
        "SELECT id FROM guia_aprendizaje WHERE id_actividad_aprendizaje = ?", (act_id,)
    ).fetchone()

    if existing:
        db.execute(
            "UPDATE guia_aprendizaje SET url = ?, subido_en = CURRENT_TIMESTAMP WHERE id_actividad_aprendizaje = ?",
            (url, act_id),
        )
    else:
        db.execute(
            "INSERT INTO guia_aprendizaje (id_actividad_aprendizaje, url) VALUES (?, ?)",
            (act_id, url),
        )
    db.commit()
    return jsonify({"ok": True})


@app.post("/api/instructor/actividad/<int:act_id>/evidencia")
@role_required("Instructor")
def api_instructor_evidencia_crear(act_id):
    data = request.get_json() or {}
    descripcion = data.get("descripcion", "").strip() or None

    db = get_db()
    existing = db.execute(
        "SELECT id FROM evidencia_aprendizaje WHERE id_actividad_aprendizaje = ?", (act_id,)
    ).fetchone()

    if existing:
        return jsonify({"ok": True, "id": existing["id"], "already_exists": True})

    cursor = db.execute(
        "INSERT INTO evidencia_aprendizaje (id_actividad_aprendizaje, descripcion) VALUES (?, ?)",
        (act_id, descripcion),
    )
    db.commit()
    return jsonify({"ok": True, "id": cursor.lastrowid})


@app.route("/api/instructor/actividad/<int:act_id>/aprendices")
@role_required("Instructor")
def api_instructor_aprendices(act_id):
    db = get_db()
    row = db.execute(
        """
        SELECT f.id AS ficha_id, f.numero AS ficha_numero
        FROM actividad_aprendizaje aa
        JOIN actividad_proyecto ap ON ap.id = aa.id_actividad_proyecto
        JOIN fase_proyecto fp ON fp.id = ap.id_fase_proyecto
        JOIN ficha_formacion f ON f.id_proyecto_formativo = fp.id_proyecto_formativo
        WHERE aa.id = ?
        LIMIT 1
        """,
        (act_id,),
    ).fetchone()

    if row is None:
        return jsonify({"aprendices": [], "evidencia_id": None})

    evidencia = db.execute(
        "SELECT id FROM evidencia_aprendizaje WHERE id_actividad_aprendizaje = ?", (act_id,)
    ).fetchone()

    aprendices_raw = db.execute(
        """
        SELECT a.id, a.nombres, a.apellidos, a.documento,
               u.id AS usuario_id, u.correo
        FROM aprendiz a
        LEFT JOIN usuario u ON lower(u.nombre) = lower(a.nombres || ' ' || a.apellidos)
                           AND u.rol = 'Aprendiz'
        WHERE a.ficha = ?
        ORDER BY a.nombres ASC, a.apellidos ASC
        """,
        (row["ficha_numero"],),
    ).fetchall()

    result = []
    for ap in aprendices_raw:
        entrega = None
        if evidencia and ap["usuario_id"]:
            entrega_row = db.execute(
                """
                SELECT id, url, calificacion, observaciones, entregado_en
                FROM entrega_evidencia
                WHERE id_evidencia_aprendizaje = ? AND id_usuario = ?
                """,
                (evidencia["id"], ap["usuario_id"]),
            ).fetchone()
            if entrega_row:
                entrega = {
                    "id": entrega_row["id"],
                    "url": entrega_row["url"],
                    "calificacion": entrega_row["calificacion"],
                    "observaciones": entrega_row["observaciones"],
                    "entregado_en": entrega_row["entregado_en"],
                }

        result.append(
            {
                "id": ap["id"],
                "nombre": f"{ap['nombres']} {ap['apellidos']}",
                "documento": ap["documento"],
                "usuario_id": ap["usuario_id"],
                "correo": ap["correo"],
                "entrega": entrega,
            }
        )

    return jsonify({"aprendices": result, "evidencia_id": evidencia["id"] if evidencia else None})


@app.post("/api/instructor/entrega/<int:entrega_id>/calificar")
@role_required("Instructor")
def api_instructor_calificar(entrega_id):
    data = request.get_json() or {}
    calificacion = data.get("calificacion")
    observaciones = data.get("observaciones", "").strip() or None

    if calificacion is None:
        return jsonify({"ok": False, "error": "Calificación requerida"}), 400
    try:
        calificacion = float(calificacion)
        if not (0 <= calificacion <= 100):
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "La calificación debe ser un número entre 0 y 100"}), 400

    db = get_db()
    db.execute(
        "UPDATE entrega_evidencia SET calificacion = ?, observaciones = ? WHERE id = ?",
        (calificacion, observaciones, entrega_id),
    )
    db.commit()
    return jsonify({"ok": True, "aprobado": calificacion >= 75})


@app.post("/api/instructor/ficha/<int:ficha_id>/fase/nueva")
@role_required("Instructor")
def api_instructor_fase_nueva(ficha_id):
    data = request.get_json() or {}
    nombre = data.get("nombre", "").strip()
    if not nombre:
        return jsonify({"ok": False, "error": "Nombre requerido"}), 400

    db = get_db()
    ficha = db.execute(
        "SELECT id_proyecto_formativo FROM ficha_formacion WHERE id = ?", (ficha_id,)
    ).fetchone()
    if ficha is None or ficha["id_proyecto_formativo"] is None:
        return jsonify({"ok": False, "error": "Ficha no tiene proyecto formativo"}), 400

    cursor = db.execute(
        "INSERT INTO fase_proyecto (id_proyecto_formativo, nombre) VALUES (?, ?)",
        (ficha["id_proyecto_formativo"], nombre),
    )
    db.commit()
    return jsonify({"ok": True, "id": cursor.lastrowid, "nombre": nombre})


@app.post("/api/instructor/fase/<int:fase_id>/actividad/nueva")
@role_required("Instructor")
def api_instructor_actividad_nueva(fase_id):
    data = request.get_json() or {}
    nombre = data.get("nombre", "").strip()
    if not nombre:
        return jsonify({"ok": False, "error": "Nombre requerido"}), 400

    db = get_db()
    cursor = db.execute(
        "INSERT INTO actividad_proyecto (id_fase_proyecto, nombre) VALUES (?, ?)",
        (fase_id, nombre),
    )
    db.commit()
    return jsonify({"ok": True, "id": cursor.lastrowid, "nombre": nombre})


@app.post("/api/instructor/actividad-proyecto/<int:act_proy_id>/aprendizaje/nueva")
@role_required("Instructor")
def api_instructor_act_aprendizaje_nueva(act_proy_id):
    data = request.get_json() or {}
    nombre = data.get("nombre", "").strip()
    if not nombre:
        return jsonify({"ok": False, "error": "Nombre requerido"}), 400

    db = get_db()
    cursor = db.execute(
        "INSERT INTO actividad_aprendizaje (id_actividad_proyecto, nombre) VALUES (?, ?)",
        (act_proy_id, nombre),
    )
    db.commit()
    return jsonify({"ok": True, "id": cursor.lastrowid, "nombre": nombre})


if __name__ == "__main__":
    app.run(debug=True)
