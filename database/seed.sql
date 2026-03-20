-- ============================================================
-- Project    : bariLMS — Learning Management System (SENA)
-- File       : database/seed.sql
-- Description: Datos de referencia y catálogos base del sistema.
--              Aplicar DESPUÉS del schema principal.
--
-- How to apply:
--   psql -U <user> -d <dbname> -f database/seed.sql
--   (safe to re-run; todos los INSERT usan ON CONFLICT DO NOTHING)
--
-- Contenido:
--   1. tipo_documento           — tipos de documento colombianos
--   2. tipo_invalidacion_sesion — motivos de revocación de sesión
--   3. perfil                   — perfiles del sistema con rutas
--   4. nivel_formacion          — niveles de formación SENA
--   5. fase                     — fases del proceso formativo
-- ============================================================

BEGIN;

-- ============================================================
-- 1. TIPOS DE DOCUMENTO (Colombia)
-- ============================================================
-- Documentos de identidad vigentes reconocidos por la RNEC y la DIAN.
-- El campo codigo usa COLLATE "C" (definido en el schema).

INSERT INTO tipo_documento (id, codigo, nombre, descripcion) VALUES
    (gen_random_uuid(), 'CC',   'Cédula de Ciudadanía',
        'Documento de identidad para ciudadanos colombianos mayores de 18 años.'),

    (gen_random_uuid(), 'TI',   'Tarjeta de Identidad',
        'Documento de identidad para menores colombianos entre 7 y 17 años.'),

    (gen_random_uuid(), 'RC',   'Registro Civil de Nacimiento',
        'Documento de identidad para menores de 7 años o trámites civiles.'),

    (gen_random_uuid(), 'CE',   'Cédula de Extranjería',
        'Documento para extranjeros con residencia en Colombia.'),

    (gen_random_uuid(), 'PA',   'Pasaporte',
        'Documento de viaje internacional; aceptado como identificación.'),

    (gen_random_uuid(), 'NIT',  'Número de Identificación Tributaria',
        'Identificación fiscal de personas jurídicas y empresas ante la DIAN.'),

    (gen_random_uuid(), 'PEP',  'Permiso Especial de Permanencia',
        'Documento para ciudadanos venezolanos en Colombia (Resolución 740/2018).'),

    (gen_random_uuid(), 'PPT',  'Permiso por Protección Temporal',
        'Documento para venezolanos bajo el Estatuto Temporal de Protección (Decreto 216/2021).'),

    (gen_random_uuid(), 'NUIP', 'Número Único de Identificación Personal',
        'Número asignado al nacer; migra a CC/TI al cumplir la mayoría de edad.')

ON CONFLICT (codigo) DO NOTHING;


-- ============================================================
-- 2. TIPOS DE INVALIDACIÓN DE SESIÓN
-- ============================================================
-- Catálogo de motivos por los que una sesión puede ser revocada.
-- La app registra tipo_invalidacion_id en sesion al invalidarla
-- y escribe un evento 'revoked' en sesion_historial.

INSERT INTO tipo_invalidacion_sesion (id, codigo, nombre, descripcion) VALUES
    (gen_random_uuid(), 'logout_manual',
        'Cierre de sesión voluntario',
        'El usuario cerró sesión de forma explícita desde la interfaz.'),

    (gen_random_uuid(), 'expiracion_refresh',
        'Refresh token expirado',
        'El refresh token superó su tiempo de vida de 1 día sin ser renovado.'),

    (gen_random_uuid(), 'token_reutilizado',
        'Reutilización de refresh token',
        'Se detectó un intento de reuso del refresh token ya rotado. '
        'Indica posible robo de sesión; todas las sesiones del usuario son revocadas.'),

    (gen_random_uuid(), 'logout_todos_dispositivos',
        'Cierre de sesión en todos los dispositivos',
        'El usuario solicitó cerrar todas sus sesiones activas simultáneamente.'),

    (gen_random_uuid(), 'admin_revocado',
        'Revocación por administrador',
        'Un administrador invalidó la sesión manualmente (ej.: actividad sospechosa).'),

    (gen_random_uuid(), 'cuenta_desactivada',
        'Cuenta de usuario desactivada',
        'La cuenta fue desactivada (usuario.activo = FALSE); '
        'todas sus sesiones activas se revocan automáticamente.'),

    (gen_random_uuid(), 'cambio_contrasena',
        'Cambio de contraseña',
        'El usuario cambió su contraseña; todas las sesiones previas '
        'son invalidadas por seguridad.'),

    (gen_random_uuid(), 'sesion_duplicada',
        'Sesión duplicada desde el mismo dispositivo',
        'Se creó una nueva sesión desde el mismo user_agent/IP '
        'cuando ya existía una activa en ese dispositivo.')

ON CONFLICT (codigo) DO NOTHING;


-- ============================================================
-- 3. PERFILES DEL SISTEMA
-- ============================================================
-- Cada perfil tiene su ruta exclusiva de dashboard.
-- Solo usuarios con usuario_perfil apuntando a ese perfil pueden acceder.
-- Si el usuario tiene un único perfil → redirige directo a ruta_dashboard.
-- Si tiene varios → la app muestra un selector antes de redirigir.

INSERT INTO perfil (id, nombre, descripcion, ruta_dashboard) VALUES
    (gen_random_uuid(), 'Administrador',
        'Gestión completa: usuarios, estructura institucional y académica.',
        '/dashboard/administrador'),

    (gen_random_uuid(), 'Administrativo',
        'Apoyo académico y operativo: fichas, programas, ambientes y sedes.',
        '/dashboard/administrativo'),

    (gen_random_uuid(), 'Instructor',
        'Ejecución formativa: fichas asignadas, fases, actividades y calificaciones.',
        '/dashboard/instructor'),

    (gen_random_uuid(), 'Aprendiz',
        'Ruta de aprendizaje: fichas, entrega de evidencias y seguimiento de notas.',
        '/dashboard/aprendiz'),

    (gen_random_uuid(), 'Empresa',
        'Acceso empresarial: seguimiento de aprendices en etapa productiva '
        'y gestión de contratos de aprendizaje.',
        '/dashboard/empresa')

ON CONFLICT (nombre) DO NOTHING;


-- ============================================================
-- 4. NIVELES DE FORMACIÓN
-- ============================================================

INSERT INTO nivel_formacion (id, nombre) VALUES
    (gen_random_uuid(), 'Técnico'),
    (gen_random_uuid(), 'Tecnólogo'),
    (gen_random_uuid(), 'Operario'),
    (gen_random_uuid(), 'Auxiliar'),
    (gen_random_uuid(), 'Curso')
ON CONFLICT (nombre) DO NOTHING;


-- ============================================================
-- 5. FASES DEL PROCESO FORMATIVO
-- ============================================================

INSERT INTO fase (id, nombre, orden, descripcion) VALUES
    (gen_random_uuid(), 'Análisis',   1,
        'Identificación del proyecto formativo y reconocimiento del entorno productivo.'),
    (gen_random_uuid(), 'Planeación', 2,
        'Diseño y estructuración de las actividades del proyecto formativo.'),
    (gen_random_uuid(), 'Ejecución',  3,
        'Desarrollo de las actividades y entrega de evidencias de aprendizaje.')
ON CONFLICT (nombre) DO NOTHING;

COMMIT;
