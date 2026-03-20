"""Inicialización de la base de datos: migraciones legacy y admin provisional."""

import secrets
import string
import uuid

from bari_lms.db import get_db
from bari_lms.services.security import hash_password

# ── Tablas renombradas en el esquema legacy ─────────────────────────────────
_LEGACY_TABLE_NAMES = {
    "users": "usuario",
    "regionales": "regional",
    "centros": "centro",
    "coordinaciones": "coordinacion",
    "sedes": "sede",
    "instructores": "instructor",
    "aprendices": "aprendiz",
    "ambientes": "ambiente",
}

# ── Columnas renombradas en el esquema legacy ────────────────────────────────
_COLUMN_RENAMES = {
    "usuario": {
        "email": "correo",
        "password_hash": "contrasena_hash",
        "role": "rol",
        "name": "nombre",
        "active": "activo",
        "created_at": "creado_en",
    },
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
    "entrega_evidencia": {
        "id_evidencia_aprendizaje": "evidencia_aprendizaje_id",
        "id_usuario": "usuario_id",
    },
    "seccion_actividad": {"id_actividad_aprendizaje": "actividad_aprendizaje_id"},
    "sub_seccion_actividad": {"id_seccion": "seccion_id"},
    "guia_actividad_proyecto": {"id_actividad_proyecto": "actividad_proyecto_id"},
    "ficha_instructor_competencia": {
        "id_ficha": "ficha_id",
        "id_instructor": "instructor_id",
    },
    "asistencia_aprendiz": {"id_ficha": "ficha_id", "id_aprendiz": "aprendiz_id"},
}


def _get_existing_tables(db):
    return {
        row["name"]
        for row in db.execute(
            "SELECT tablename AS name FROM pg_tables WHERE schemaname = 'public'"
        ).fetchall()
    }


def _get_table_columns(db, table_name):
    return {
        row["name"]
        for row in db.execute(
            "SELECT column_name AS name FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = ?",
            (table_name,),
        ).fetchall()
    }


def _run_legacy_migrations(db):
    """Renombra tablas y columnas del esquema antiguo."""
    existing = _get_existing_tables(db)

    for old_name, new_name in _LEGACY_TABLE_NAMES.items():
        if old_name in existing and new_name not in existing:
            db.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")
            existing.discard(old_name)
            existing.add(new_name)

    for table_name, rename_map in _COLUMN_RENAMES.items():
        if table_name not in existing:
            continue
        cols = _get_table_columns(db, table_name)
        for old_col, new_col in rename_map.items():
            if old_col in cols and new_col not in cols:
                db.execute(
                    f"ALTER TABLE {table_name} RENAME COLUMN {old_col} TO {new_col}"
                )
                cols.discard(old_col)
                cols.add(new_col)

    db.commit()


def _generate_password(length=12):
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _provision_admin(db):
    """Crea un administrador provisional si no existe ninguno con ese perfil."""
    row = db.execute(
        """
        SELECT COUNT(*) AS total
        FROM usuario_perfil up
        JOIN perfil p ON p.id = up.perfil_id
        WHERE p.nombre = 'Administrador'
        """
    ).fetchone()
    if row and row["total"] > 0:
        return

    temp_email = f"admin_{secrets.token_hex(4)}@senalearn.edu.co"
    temp_password = _generate_password()
    user_id = str(uuid.uuid7())

    db.execute(
        "INSERT INTO usuario (id, correo, contrasena_hash, nombre, activo) "
        "VALUES (?, ?, ?, ?, TRUE)",
        (user_id, temp_email, hash_password(temp_password), "Admin Provisional"),
    )
    db.execute(
        """
        INSERT INTO usuario_perfil (id, usuario_id, perfil_id)
        SELECT ?, ?, p.id FROM perfil p WHERE p.nombre = 'Administrador'
        """,
        (str(uuid.uuid7()), user_id),
    )
    db.commit()

    print()
    print("[bariLMS] ⚠  No se encontró ningún administrador.")
    print(f"[bariLMS]    Correo     : {temp_email}")
    print(f"[bariLMS]    Contraseña : {temp_password}")
    print("[bariLMS]    Úsalas para el primer acceso y crea tu cuenta real de inmediato.")
    print()


def initialize_database():
    """Aplica migraciones legacy y provisiona el admin si no existe."""
    db = get_db()
    _run_legacy_migrations(db)
    _provision_admin(db)
