"""Repositorio de usuario: consultas sobre autenticación, perfiles y listados."""

import copy

from bari_lms.config import DASHBOARDS
from bari_lms.db import get_db


def get_user_by_email(email):
    if not email:
        return None
    return get_db().execute(
        """
        SELECT u.id, u.correo_institucional AS email,
               COALESCE(pe.nombres || ' ' || pe.apellidos, u.correo_institucional) AS name,
               u.activo AS active,
               u.creado_en AS created_at, u.contrasena_hash AS password_hash
        FROM usuario u
        LEFT JOIN persona pe ON pe.id = u.id
        WHERE lower(u.correo_institucional) = lower(?)
        """,
        (email,),
    ).fetchone()


def user_has_profile(user_id, profile_name):
    row = get_db().execute(
        """
        SELECT 1
        FROM usuario_perfil up
        JOIN perfil p ON p.id = up.perfil_id
        WHERE up.usuario_id = ? AND p.nombre = ?
        """,
        (user_id, profile_name),
    ).fetchone()
    return row is not None


def get_user_by_id(user_id):
    return get_db().execute(
        """
        SELECT u.id, u.correo_institucional AS email,
               COALESCE(pe.nombres || ' ' || pe.apellidos, u.correo_institucional) AS name,
               u.activo AS active,
               u.creado_en AS created_at,
               (SELECT p.nombre FROM usuario_perfil up
                JOIN perfil p ON p.id = up.perfil_id
                WHERE up.usuario_id = u.id LIMIT 1) AS role
        FROM usuario u
        LEFT JOIN persona pe ON pe.id = u.id
        WHERE u.id = ?
        """,
        (user_id,),
    ).fetchone()


def get_all_users():
    return get_db().execute(
        """
        SELECT u.id, u.correo_institucional AS email,
               COALESCE(pe.nombres || ' ' || pe.apellidos, u.correo_institucional) AS name,
               u.activo AS active,
               u.creado_en AS created_at,
               (SELECT p.nombre FROM usuario_perfil up
                JOIN perfil p ON p.id = up.perfil_id
                WHERE up.usuario_id = u.id LIMIT 1) AS role
        FROM usuario u
        LEFT JOIN persona pe ON pe.id = u.id
        ORDER BY u.creado_en DESC, u.id DESC
        """
    ).fetchall()


def get_admin_dashboard_data():
    db = get_db()
    total_active = db.execute(
        "SELECT COUNT(*) AS total FROM usuario WHERE activo = TRUE"
    ).fetchone()["total"]
    total_roles = db.execute(
        "SELECT COUNT(DISTINCT perfil_id) AS total FROM usuario_perfil"
    ).fetchone()["total"]
    total_regionales = db.execute(
        "SELECT COUNT(*) AS total FROM regional"
    ).fetchone()["total"]
    total_centros = db.execute(
        "SELECT COUNT(*) AS total FROM centro"
    ).fetchone()["total"]
    latest_users = db.execute(
        """
        SELECT COALESCE(pe.nombres || ' ' || pe.apellidos, u.correo_institucional) AS name,
               u.correo_institucional AS email,
               (SELECT p.nombre FROM usuario_perfil up
                JOIN perfil p ON p.id = up.perfil_id
                WHERE up.usuario_id = u.id LIMIT 1) AS role
        FROM usuario u
        LEFT JOIN persona pe ON pe.id = u.id
        ORDER BY u.creado_en DESC, u.id DESC
        LIMIT 3
        """
    ).fetchall()

    config = copy.deepcopy(DASHBOARDS["administrador"])
    config["metrics"][0]["value"] = str(total_active)
    config["metrics"][1]["value"] = str(total_regionales)
    config["metrics"][2]["value"] = str(total_roles)
    config["metrics"][3]["value"] = str(total_centros)
    config["table_title"] = "Últimos usuarios registrados"
    config["table_headers"] = ["Nombre", "Rol", "Correo"]
    config["table_rows"] = (
        [[row["name"], row["role"], row["email"]] for row in latest_users]
        or [["Sin registros", "-", "-"]]
    )
    return config
