"""
Proyecto    : bariLMS — Sistema de Gestión del Aprendizaje (SENA)
Archivo     : database/seed.py
Descripción : Datos de referencia y catálogos base del sistema.
              Aplicar DESPUÉS del esquema principal.

Uso:
    python database/seed.py

Requiere .env con PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD.

Contenido:
    1. sexo                     — sexo biológico
    2. tipo_documento           — tipos de documento colombianos
    3. tipo_invalidacion_sesion — motivos de revocación de sesión
    4. perfil                   — perfiles del sistema con rutas
    5. rol                      — rol por defecto por perfil
    6. nivel_formacion          — niveles de formación SENA
    7. fase                     — fases del proceso formativo
"""

import os
import uuid_utils as uuid

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_conn():
    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=int(os.environ.get("PGPORT", 5432)),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ.get("PGPASSWORD", ""),
    )


def uid() -> str:
    return str(uuid.uuid7())


def seed(conn):
    with conn.cursor() as cur:

        # ── 1. Sexo biológico ────────────────────────────────────────────────
        cur.executemany(
            "INSERT INTO sexo (id, codigo, nombre) VALUES (%s, %s, %s) "
            "ON CONFLICT (codigo) DO NOTHING",
            [
                (uid(), "M", "Masculino"),
                (uid(), "F", "Femenino"),
            ],
        )

        # ── 2. Tipos de documento (Colombia) ────────────────────────────────
        cur.executemany(
            "INSERT INTO tipo_documento (id, codigo, nombre, descripcion) "
            "VALUES (%s, %s, %s, %s) ON CONFLICT (codigo) DO NOTHING",
            [
                (uid(), "CC",   "Cédula de Ciudadanía",
                 "Documento de identidad para ciudadanos colombianos mayores de 18 años."),
                (uid(), "TI",   "Tarjeta de Identidad",
                 "Documento de identidad para menores colombianos entre 7 y 17 años."),
                (uid(), "RC",   "Registro Civil de Nacimiento",
                 "Documento de identidad para menores de 7 años o trámites civiles."),
                (uid(), "CE",   "Cédula de Extranjería",
                 "Documento para extranjeros con residencia en Colombia."),
                (uid(), "PA",   "Pasaporte",
                 "Documento de viaje internacional; aceptado como identificación."),
                (uid(), "NIT",  "Número de Identificación Tributaria",
                 "Identificación fiscal de personas jurídicas y empresas ante la DIAN."),
                (uid(), "PEP",  "Permiso Especial de Permanencia",
                 "Documento para ciudadanos venezolanos en Colombia (Resolución 740/2018)."),
                (uid(), "PPT",  "Permiso por Protección Temporal",
                 "Documento para venezolanos bajo el Estatuto Temporal de Protección (Decreto 216/2021)."),
                (uid(), "NUIP", "Número Único de Identificación Personal",
                 "Número asignado al nacer; migra a CC o TI al cumplir la mayoría de edad."),
            ],
        )

        # ── 3. Tipos de invalidación de sesión ──────────────────────────────
        cur.executemany(
            "INSERT INTO tipo_invalidacion_sesion (id, codigo, nombre, descripcion) "
            "VALUES (%s, %s, %s, %s) ON CONFLICT (codigo) DO NOTHING",
            [
                (uid(), "logout_manual",
                 "Cierre de sesión voluntario",
                 "El usuario cerró sesión de forma explícita desde la interfaz."),
                (uid(), "expiracion_refresh",
                 "Refresh token expirado",
                 "El refresh token superó su tiempo de vida de 1 día sin ser renovado."),
                (uid(), "token_reutilizado",
                 "Reutilización de refresh token",
                 "Se detectó un intento de reuso del refresh token ya rotado. "
                 "Indica posible robo de sesión; se revocan todas las sesiones del usuario."),
                (uid(), "logout_todos_dispositivos",
                 "Cierre de sesión en todos los dispositivos",
                 "El usuario solicitó cerrar todas sus sesiones activas simultáneamente."),
                (uid(), "admin_revocado",
                 "Revocación por administrador",
                 "Un administrador invalidó la sesión manualmente."),
                (uid(), "cuenta_desactivada",
                 "Cuenta de usuario desactivada",
                 "La cuenta fue desactivada (usuario.activo = FALSE); "
                 "todas sus sesiones activas se revocan automáticamente."),
                (uid(), "cambio_contrasena",
                 "Cambio de contraseña",
                 "El usuario cambió su contraseña; todas las sesiones previas "
                 "son invalidadas por seguridad."),
                (uid(), "sesion_duplicada",
                 "Sesión duplicada desde el mismo dispositivo",
                 "Se creó una nueva sesión desde el mismo user_agent/IP "
                 "cuando ya existía una activa en ese dispositivo."),
            ],
        )

        # ── 4. Perfiles del sistema ──────────────────────────────────────────
        cur.executemany(
            "INSERT INTO perfil (id, nombre, descripcion, ruta_dashboard) "
            "VALUES (%s, %s, %s, %s) ON CONFLICT (nombre) DO NOTHING",
            [
                (uid(), "Administrador",
                 "Gestión completa: usuarios, estructura institucional y académica.",
                 "/dashboard/administrador"),
                (uid(), "Administrativo",
                 "Apoyo académico y operativo: fichas, programas, ambientes y sedes.",
                 "/dashboard/administrativo"),
                (uid(), "Instructor",
                 "Ejecución formativa: fichas asignadas, fases, actividades y calificaciones.",
                 "/dashboard/instructor"),
                (uid(), "Aprendiz",
                 "Ruta de aprendizaje: fichas, entrega de evidencias y seguimiento de notas.",
                 "/dashboard/aprendiz"),
                (uid(), "Empresa",
                 "Acceso empresarial: seguimiento de aprendices en etapa productiva "
                 "y gestión de contratos de aprendizaje.",
                 "/dashboard/empresa"),
            ],
        )

        # ── 5. Roles por defecto (uno por perfil) ───────────────────────────
        cur.execute("SELECT id, nombre FROM perfil")
        perfiles = cur.fetchall()
        cur.executemany(
            """
            INSERT INTO rol (id, perfil_id, nombre, descripcion)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (perfil_id, nombre) DO NOTHING
            """,
            [
                (
                    uid(),
                    perfil_id,
                    nombre,
                    f"Rol base del perfil {nombre}. "
                    "Punto de partida para la asignación de permisos.",
                )
                for perfil_id, nombre in perfiles
            ],
        )

        # ── 6. Niveles de formación ──────────────────────────────────────────
        cur.executemany(
            "INSERT INTO nivel_formacion (id, nombre) VALUES (%s, %s) "
            "ON CONFLICT (nombre) DO NOTHING",
            [
                (uid(), "Técnico"),
                (uid(), "Tecnólogo"),
                (uid(), "Operario"),
                (uid(), "Auxiliar"),
                (uid(), "Curso"),
            ],
        )

        # ── 7. Fases del proceso formativo ──────────────────────────────────
        cur.executemany(
            "INSERT INTO fase (id, nombre, orden, descripcion) VALUES (%s, %s, %s, %s) "
            "ON CONFLICT (nombre) DO NOTHING",
            [
                (uid(), "Análisis",   1,
                 "Identificación del proyecto formativo y reconocimiento del entorno productivo."),
                (uid(), "Planeación", 2,
                 "Diseño y estructuración de las actividades del proyecto formativo."),
                (uid(), "Ejecución",  3,
                 "Desarrollo de las actividades y entrega de evidencias de aprendizaje."),
            ],
        )

    conn.commit()
    print("Seed completado.")


if __name__ == "__main__":
    with get_conn() as conn:
        seed(conn)
