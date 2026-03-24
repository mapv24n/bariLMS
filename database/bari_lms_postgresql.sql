-- ============================================================
-- Proyecto    : bariLMS — Sistema de Gestión del Aprendizaje (SENA)
-- Archivo     : database/bari_lms_postgresql.sql
-- Descripción : Esquema canónico PostgreSQL de bariLMS.
--               Reemplaza database/setup_aprendiz.sql (legacy).
--
-- PostgreSQL  : Requiere PostgreSQL 17+
--
-- Cómo aplicar:
--   1. psql -U <usuario> -d <base> -f database/bari_lms_postgresql.sql
--   2. psql -U <usuario> -d <base> -f database/seed.sql
--   (seguro re-ejecutar; todo el DDL usa IF NOT EXISTS)
--
-- ── UUID v7 ──────────────────────────────────────────────────
--   Generado por la capa de aplicación.
--   Ninguna columna id tiene DEFAULT — la app siempre los provee.
--   sesion.id duplica como claim jti en AMBOS tokens (access y
--   refresh). Invalidar la fila sesion revoca ambos tokens a la vez.
--
-- ── actualizado_en ───────────────────────────────────────────
--   DEFAULT NULL — permanece NULL hasta el primer UPDATE.
--   Explícito en cada tabla para mayor claridad.
--
-- ── creado_por ───────────────────────────────────────────────
--   NULL para el admin provisional y filas de catálogo.
--   ON DELETE SET NULL — las filas de auditoría nunca quedan
--   huérfanas al borrar el usuario creador.
--
-- ── COLLATE "C" ──────────────────────────────────────────────
--   Aplicado a códigos, hashes, correos y números de documento
--   (ASCII / minúsculas). Índices con comparación byte a byte:
--   más rápido y sin reglas de locale. Las columnas de texto
--   libre en español usan la collation por defecto de la DB.
--
-- ── Reglas de mayúsculas/minúsculas (CHECK) ──────────────────
--   correo_institucional, correo_personal → siempre lower().
--   persona.nombres, persona.apellidos    → siempre UPPER().
--
-- ── Personas y cuentas ───────────────────────────────────────
--   usuario  — ancla de autenticación (correo + contraseña).
--              El admin provisional vive aquí sin fila en persona.
--              No tiene columna nombre: el nombre se obtiene de
--              persona.nombres/apellidos; para el admin provisional
--              la app usa el correo_institucional como identificador.
--   persona  — datos personales e identidad del usuario real.
--              persona.id = usuario.id (PK compartida, relación 1:1).
--              No existe columna usuario_id: persona.id ES la FK.
--              correo_personal vive aquí, no en usuario.
--   instructor, aprendiz, personal_administrativo — datos del rol.
--              Cada uno referencia persona con persona_id NOT NULL UNIQUE.
--              Para llegar al usuario: persona.id = usuario.id (mismo UUID).
--
-- ── Enrutamiento de dashboard (capa de aplicación) ───────────
--   /dashboard → un perfil: redirige a perfil.ruta_dashboard.
--                varios perfiles: muestra selector primero.
--   /dashboard/<slug> → bloqueado a menos que usuario_perfil
--   vincule al usuario autenticado con ese perfil.
--
-- ── JWT / cookies (capa de aplicación) ───────────────────────
--   Cookies: HttpOnly, Secure, SameSite=Strict.
--   access_token  : 15 min, JWT typ=access, NO se guarda en DB.
--   refresh_token : 1 día,  JWT typ=refresh, hash Argon2 en sesion.
--   Ambos llevan el mismo jti = sesion.id (UUID v7).
--   Validación access : firma → typ → exp → sesion activa.
--   Validación refresh: firma → typ → exp → sesion activa → Argon2.
--   Hash incorrecto en refresh → revocar con tipo=token_reutilizado.
--   Con éxito: rotar hash, emitir nuevo access token.
--
-- ── Admin provisional (capa de aplicación) ───────────────────
--   Al arrancar sin ningún usuario Administrador: crear una fila
--   en usuario con correo_institucional y contraseña aleatorios,
--   imprimir en stdout una sola vez. No se crea fila en persona.
--
-- ── Tablas (orden de dependencia) ────────────────────────────
--   Catálogos : tipo_documento, tipo_invalidacion_sesion, sexo
--   Auth      : usuario, persona, sesion, sesion_historial
--   Acceso    : perfil, rol, permiso, rol_permiso,
--               usuario_perfil, usuario_rol
--   Estructura: regional, centro, coordinacion, sede, ambiente
--   Académico : red_conocimiento, area, nivel_formacion
--   Personas  : instructor, aprendiz, personal_administrativo
--   Contenido : proyecto_formativo, fase_proyecto, actividad_proyecto,
--               actividad_aprendizaje, guia_aprendizaje,
--               evidencia_aprendizaje, entrega_evidencia,
--               seccion_actividad, sub_seccion_actividad,
--               guia_actividad_proyecto
--   Programas : programa_formacion, ficha_formacion,
--               ficha_instructor_competencia, asistencia_aprendiz
--   Extras    : fase, notificacion
-- ============================================================

BEGIN;

-- ============================================================
-- CATÁLOGOS
-- ============================================================

-- Tipos de documento de identidad colombianos.
CREATE TABLE IF NOT EXISTS tipo_documento (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- código y visualización
    codigo         TEXT        COLLATE "C" NOT NULL UNIQUE,
    nombre         TEXT        NOT NULL,
    descripcion    TEXT,

    -- estado
    activo         BOOLEAN     NOT NULL DEFAULT TRUE,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_tipo_documento_codigo ON tipo_documento (codigo);


-- Catálogo de motivos de invalidación de sesión.
-- Permite auditar por qué se revocó cada sesión.
CREATE TABLE IF NOT EXISTS tipo_invalidacion_sesion (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- código y visualización
    codigo         TEXT        COLLATE "C" NOT NULL UNIQUE,
    nombre         TEXT        NOT NULL,
    descripcion    TEXT,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_tipo_invalidacion_sesion_codigo ON tipo_invalidacion_sesion (codigo);


-- Catálogo de sexo biológico. Usado en datos personales (persona).
CREATE TABLE IF NOT EXISTS sexo (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- código y visualización
    codigo         TEXT        COLLATE "C" NOT NULL UNIQUE,
    nombre         TEXT        NOT NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_sexo_codigo ON sexo (codigo);

-- ============================================================
-- AUTENTICACIÓN
-- ============================================================

-- Entidad de autenticación. Todos los perfiles tienen una fila aquí.
-- El admin provisional vive aquí sin fila en persona.
CREATE TABLE IF NOT EXISTS usuario (
    -- identidad
    id                   UUID        PRIMARY KEY,

    -- auditoría
    creado_por           UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- credenciales
    correo               TEXT        COLLATE "C" UNIQUE NOT NULL,
    contrasena_hash      TEXT        NOT NULL,

    -- datos básicos (nombre completo para el admin provisional y visualización)
    nombre               TEXT,

    -- estado
    activo               BOOLEAN     NOT NULL DEFAULT TRUE,

    -- marcas de tiempo
    creado_en            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en       TIMESTAMPTZ DEFAULT NULL,

    -- restricciones
    CHECK (correo = lower(correo))
);

CREATE INDEX IF NOT EXISTS idx_usuario_correo    ON usuario (correo);
CREATE INDEX IF NOT EXISTS idx_usuario_creado_por ON usuario (creado_por);


-- Datos personales e identidad del usuario real.
-- persona.id = usuario.id (PK compartida). No hay columna usuario_id
-- separada: persona.id ES la FK a usuario. Relación 1:1 estricta.
-- ON DELETE RESTRICT: no se puede borrar un usuario con persona activa
-- (primero hay que eliminar instructor/aprendiz/personal_administrativo).
CREATE TABLE IF NOT EXISTS persona (
    -- identidad compartida con usuario (mismo UUID v7)
    id                UUID        PRIMARY KEY REFERENCES usuario(id) ON DELETE RESTRICT,

    -- auditoría
    creado_por        UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- documento de identidad
    tipo_documento_id UUID        REFERENCES tipo_documento(id) ON DELETE RESTRICT,
    numero_documento  TEXT        COLLATE "C",

    -- datos personales
    nombres           TEXT        NOT NULL,
    apellidos         TEXT        NOT NULL,
    sexo_id           UUID        REFERENCES sexo(id) ON DELETE SET NULL,
    fecha_nacimiento  DATE,

    -- contacto
    correo_personal   TEXT        COLLATE "C",

    -- marcas de tiempo
    creado_en         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en    TIMESTAMPTZ DEFAULT NULL,

    -- restricciones
    CHECK (nombres   = upper(nombres)),
    CHECK (apellidos = upper(apellidos)),
    CHECK (correo_personal IS NULL OR correo_personal = lower(correo_personal))
);

CREATE INDEX IF NOT EXISTS idx_persona_tipo_documento_id ON persona (tipo_documento_id);
CREATE INDEX IF NOT EXISTS idx_persona_sexo_id           ON persona (sexo_id);
CREATE INDEX IF NOT EXISTS idx_persona_creado_por        ON persona (creado_por);


-- Sesiones activas. sesion.id (UUID v7) es el jti de ambos tokens.
-- refresh_token_hash : Argon2 del valor real del refresh token.
-- expira_en          : TTL de 1 día (refresh token).
-- tipo_invalidacion_id + invalidado_en: se rellenan al revocar.
CREATE TABLE IF NOT EXISTS sesion (
    -- identidad (= jti para access token y refresh token)
    id                   UUID        PRIMARY KEY,

    -- propietario
    usuario_id           UUID        NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,

    -- invalidación (NULL mientras la sesión esté activa)
    tipo_invalidacion_id UUID        REFERENCES tipo_invalidacion_sesion(id) ON DELETE RESTRICT,
    invalidado_en        TIMESTAMPTZ DEFAULT NULL,

    -- refresh token hasheado (COLLATE "C": hash ASCII)
    refresh_token_hash   TEXT        COLLATE "C" NOT NULL UNIQUE,

    -- información del cliente
    ip_address           TEXT,
    user_agent           TEXT,

    -- estado y expiración
    activo               BOOLEAN     NOT NULL DEFAULT TRUE,
    expira_en            TIMESTAMPTZ NOT NULL,

    -- marcas de tiempo
    creado_en            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en       TIMESTAMPTZ DEFAULT NULL,

    -- una sesión inactiva siempre debe tener motivo y timestamp
    CHECK (
        (activo = TRUE  AND tipo_invalidacion_id IS NULL     AND invalidado_en IS NULL)     OR
        (activo = FALSE AND tipo_invalidacion_id IS NOT NULL AND invalidado_en IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_sesion_usuario_id         ON sesion (usuario_id);
CREATE INDEX IF NOT EXISTS idx_sesion_refresh_token_hash ON sesion (refresh_token_hash);
CREATE INDEX IF NOT EXISTS idx_sesion_activo_expira      ON sesion (activo, expira_en);
CREATE INDEX IF NOT EXISTS idx_sesion_tipo_invalidacion  ON sesion (tipo_invalidacion_id);


-- Registro histórico inmutable de eventos de sesión. Nunca se borra.
-- sesion_id → SET NULL si la sesión es eliminada; el historial persiste.
-- Sin actualizado_en: registro inmutable por diseño.
CREATE TABLE IF NOT EXISTS sesion_historial (
    -- identidad
    id         UUID        PRIMARY KEY,

    -- vínculos (sesion_id puede quedar NULL si la sesión se elimina)
    sesion_id  UUID        REFERENCES sesion(id) ON DELETE SET NULL,
    usuario_id UUID        NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,

    -- evento registrado
    evento     TEXT        NOT NULL
                   CHECK (evento IN (
                       'login',
                       'logout',
                       'token_refresh',
                       'token_expired',
                       'revoked'
                   )),

    -- información del cliente (snapshot al momento del evento)
    ip_address TEXT,
    user_agent TEXT,

    -- marca de tiempo (sin actualizado_en: inmutable)
    creado_en  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sesion_historial_sesion_id  ON sesion_historial (sesion_id);
CREATE INDEX IF NOT EXISTS idx_sesion_historial_usuario_id ON sesion_historial (usuario_id);
CREATE INDEX IF NOT EXISTS idx_sesion_historial_creado_en  ON sesion_historial (creado_en);

-- ============================================================
-- CONTROL DE ACCESO
-- ============================================================

-- Perfiles del sistema con su ruta exclusiva de dashboard.
-- ruta_dashboard: cada perfil tiene su propia URL protegida.
-- Solo usuarios en usuario_perfil con ese perfil pueden acceder.
CREATE TABLE IF NOT EXISTS perfil (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- visualización
    nombre         TEXT        NOT NULL UNIQUE,
    descripcion    TEXT,

    -- enrutamiento
    ruta_dashboard TEXT        NOT NULL,

    -- auditoría
    creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_perfil_creado_por ON perfil (creado_por);


-- Roles granulares dentro de un perfil.
-- El seed crea un rol por defecto con el mismo nombre del perfil.
CREATE TABLE IF NOT EXISTS rol (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- padre
    perfil_id      UUID        NOT NULL REFERENCES perfil(id) ON DELETE CASCADE,

    -- visualización
    nombre         TEXT        NOT NULL,
    descripcion    TEXT,

    -- auditoría
    creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL,

    UNIQUE (perfil_id, nombre)
);

CREATE INDEX IF NOT EXISTS idx_rol_perfil_id  ON rol (perfil_id);
CREATE INDEX IF NOT EXISTS idx_rol_creado_por ON rol (creado_por);


-- Permisos atómicos del sistema. codigo sigue convención recurso.accion.
CREATE TABLE IF NOT EXISTS permiso (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- código y visualización
    codigo         TEXT        COLLATE "C" NOT NULL UNIQUE,
    nombre         TEXT        NOT NULL,
    descripcion    TEXT,

    -- auditoría
    creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_permiso_codigo     ON permiso (codigo);
CREATE INDEX IF NOT EXISTS idx_permiso_creado_por ON permiso (creado_por);


-- Permisos asignados a un rol.
CREATE TABLE IF NOT EXISTS rol_permiso (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- vínculos
    rol_id         UUID        NOT NULL REFERENCES rol(id)     ON DELETE CASCADE,
    permiso_id     UUID        NOT NULL REFERENCES permiso(id) ON DELETE CASCADE,

    -- auditoría
    creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL,

    UNIQUE (rol_id, permiso_id)
);

CREATE INDEX IF NOT EXISTS idx_rol_permiso_rol_id     ON rol_permiso (rol_id);
CREATE INDEX IF NOT EXISTS idx_rol_permiso_permiso_id ON rol_permiso (permiso_id);


-- Perfiles asignados a un usuario (pivote muchos-a-muchos).
CREATE TABLE IF NOT EXISTS usuario_perfil (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- vínculos
    usuario_id     UUID        NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    perfil_id      UUID        NOT NULL REFERENCES perfil(id)  ON DELETE CASCADE,

    -- auditoría
    creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL,

    UNIQUE (usuario_id, perfil_id)
);

CREATE INDEX IF NOT EXISTS idx_usuario_perfil_usuario_id ON usuario_perfil (usuario_id);
CREATE INDEX IF NOT EXISTS idx_usuario_perfil_perfil_id  ON usuario_perfil (perfil_id);


-- Roles asignados a un usuario.
CREATE TABLE IF NOT EXISTS usuario_rol (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- vínculos
    usuario_id     UUID        NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    rol_id         UUID        NOT NULL REFERENCES rol(id)     ON DELETE CASCADE,

    -- auditoría
    creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL,

    UNIQUE (usuario_id, rol_id)
);

CREATE INDEX IF NOT EXISTS idx_usuario_rol_usuario_id ON usuario_rol (usuario_id);
CREATE INDEX IF NOT EXISTS idx_usuario_rol_rol_id     ON usuario_rol (rol_id);

-- ============================================================
-- ESTRUCTURA INSTITUCIONAL
-- ============================================================

-- Regionales del SENA. Nivel más alto de la jerarquía institucional.
CREATE TABLE IF NOT EXISTS regional (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- visualización
    nombre         TEXT        NOT NULL UNIQUE,

    -- auditoría
    creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_regional_creado_por ON regional (creado_por);


-- Centros de formación. No se elimina una regional con centros (RESTRICT).
CREATE TABLE IF NOT EXISTS centro (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- padre
    regional_id    UUID        NOT NULL REFERENCES regional(id) ON DELETE RESTRICT,

    -- visualización
    nombre         TEXT        NOT NULL,

    -- auditoría
    creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_centro_regional_id ON centro (regional_id);
CREATE INDEX IF NOT EXISTS idx_centro_creado_por  ON centro (creado_por);


-- Coordinaciones académicas dentro de un centro.
CREATE TABLE IF NOT EXISTS coordinacion (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- padre
    centro_id      UUID        NOT NULL REFERENCES centro(id) ON DELETE RESTRICT,

    -- visualización
    nombre         TEXT        NOT NULL,

    -- auditoría
    creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_coordinacion_centro_id  ON coordinacion (centro_id);
CREATE INDEX IF NOT EXISTS idx_coordinacion_creado_por ON coordinacion (creado_por);


-- Sedes físicas dentro de un centro.
CREATE TABLE IF NOT EXISTS sede (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- padre
    centro_id      UUID        NOT NULL REFERENCES centro(id) ON DELETE RESTRICT,

    -- visualización
    nombre         TEXT        NOT NULL,

    -- auditoría
    creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_sede_centro_id  ON sede (centro_id);
CREATE INDEX IF NOT EXISTS idx_sede_creado_por ON sede (creado_por);


-- Ambientes o aulas dentro de una sede.
CREATE TABLE IF NOT EXISTS ambiente (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- padre
    sede_id        UUID        NOT NULL REFERENCES sede(id) ON DELETE RESTRICT,

    -- visualización
    nombre         TEXT        NOT NULL,
    capacidad      INTEGER,

    -- auditoría
    creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_ambiente_sede_id    ON ambiente (sede_id);
CREATE INDEX IF NOT EXISTS idx_ambiente_creado_por ON ambiente (creado_por);

-- ============================================================
-- ESTRUCTURA ACADÉMICA
-- ============================================================

-- Redes de conocimiento del SENA (ej: Tecnología, Agroindustria).
CREATE TABLE IF NOT EXISTS red_conocimiento (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- visualización
    nombre         TEXT        NOT NULL UNIQUE,

    -- auditoría
    creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_red_conocimiento_creado_por ON red_conocimiento (creado_por);


-- Áreas de desempeño dentro de una red de conocimiento.
CREATE TABLE IF NOT EXISTS area (
    -- identidad
    id                   UUID        PRIMARY KEY,

    -- padre
    red_conocimiento_id  UUID        NOT NULL REFERENCES red_conocimiento(id) ON DELETE RESTRICT,

    -- visualización
    nombre               TEXT        NOT NULL,

    -- auditoría
    creado_por           UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en       TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_area_red_conocimiento_id ON area (red_conocimiento_id);
CREATE INDEX IF NOT EXISTS idx_area_creado_por          ON area (creado_por);


-- Niveles de formación (Técnico, Tecnólogo, Operario, etc.).
CREATE TABLE IF NOT EXISTS nivel_formacion (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- visualización
    nombre         TEXT        NOT NULL UNIQUE,

    -- auditoría
    creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_nivel_formacion_creado_por ON nivel_formacion (creado_por);

-- ============================================================
-- PERSONAS
-- ============================================================
-- Cada tabla lleva persona_id NOT NULL UNIQUE → persona.
-- Para llegar al usuario: persona.id = usuario.id (mismo UUID).
-- ============================================================

-- Instructores vinculados a un centro y opcionalmente a un área.
-- RESTRICT en centro y área: no se borran si tienen instructores.
CREATE TABLE IF NOT EXISTS instructor (
    -- identidad
    id          UUID        PRIMARY KEY,

    -- persona (1:1 — mismo UUID que usuario vía persona)
    persona_id  UUID        NOT NULL UNIQUE REFERENCES persona(id) ON DELETE RESTRICT,

    -- institucional
    centro_id   UUID        NOT NULL REFERENCES centro(id) ON DELETE RESTRICT,
    area_id     UUID        REFERENCES area(id) ON DELETE SET NULL,

    -- auditoría
    creado_por  UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_instructor_persona_id ON instructor (persona_id);
CREATE INDEX IF NOT EXISTS idx_instructor_centro_id  ON instructor (centro_id);
CREATE INDEX IF NOT EXISTS idx_instructor_area_id    ON instructor (area_id);
CREATE INDEX IF NOT EXISTS idx_instructor_creado_por ON instructor (creado_por);


-- Aprendices vinculados a una regional.
-- RESTRICT en regional: no se borra si tiene aprendices.
CREATE TABLE IF NOT EXISTS aprendiz (
    -- identidad
    id          UUID        PRIMARY KEY,

    -- persona (1:1)
    persona_id  UUID        NOT NULL UNIQUE REFERENCES persona(id) ON DELETE RESTRICT,

    -- institucional
    regional_id UUID        NOT NULL REFERENCES regional(id) ON DELETE RESTRICT,

    -- académico
    ficha       TEXT,

    -- auditoría
    creado_por  UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_aprendiz_persona_id  ON aprendiz (persona_id);
CREATE INDEX IF NOT EXISTS idx_aprendiz_regional_id ON aprendiz (regional_id);
CREATE INDEX IF NOT EXISTS idx_aprendiz_creado_por  ON aprendiz (creado_por);


-- Personal administrativo vinculado a un centro.
-- RESTRICT en centro: no se borra si tiene personal administrativo.
CREATE TABLE IF NOT EXISTS personal_administrativo (
    -- identidad
    id          UUID        PRIMARY KEY,

    -- persona (1:1)
    persona_id  UUID        NOT NULL UNIQUE REFERENCES persona(id) ON DELETE RESTRICT,

    -- institucional
    centro_id   UUID        NOT NULL REFERENCES centro(id) ON DELETE RESTRICT,

    -- específico del rol
    cargo       TEXT        NOT NULL,

    -- auditoría
    creado_por  UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_personal_administrativo_persona_id ON personal_administrativo (persona_id);
CREATE INDEX IF NOT EXISTS idx_personal_administrativo_centro_id  ON personal_administrativo (centro_id);
CREATE INDEX IF NOT EXISTS idx_personal_administrativo_creado_por ON personal_administrativo (creado_por);

-- ============================================================
-- CADENA DE CONTENIDO ACADÉMICO
-- ============================================================

-- Proyecto formativo: documento guía del proceso de formación.
CREATE TABLE IF NOT EXISTS proyecto_formativo (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- código y visualización
    codigo         TEXT        COLLATE "C" NOT NULL UNIQUE,
    nombre         TEXT        NOT NULL,

    -- auditoría
    creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_proyecto_formativo_creado_por ON proyecto_formativo (creado_por);


-- Fases del proyecto formativo (ej: Análisis, Planeación, Ejecución).
-- CASCADE: al borrar el proyecto se borran sus fases.
CREATE TABLE IF NOT EXISTS fase_proyecto (
    -- identidad
    id                    UUID        PRIMARY KEY,

    -- padre
    proyecto_formativo_id UUID        NOT NULL REFERENCES proyecto_formativo(id) ON DELETE CASCADE,

    -- visualización
    nombre                TEXT        NOT NULL,

    -- auditoría
    creado_por            UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en        TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_fase_proyecto_proyecto_formativo_id ON fase_proyecto (proyecto_formativo_id);
CREATE INDEX IF NOT EXISTS idx_fase_proyecto_creado_por            ON fase_proyecto (creado_por);


-- Actividades del proyecto agrupadas por fase.
CREATE TABLE IF NOT EXISTS actividad_proyecto (
    -- identidad
    id               UUID        PRIMARY KEY,

    -- padre
    fase_proyecto_id UUID        NOT NULL REFERENCES fase_proyecto(id) ON DELETE CASCADE,

    -- visualización
    nombre           TEXT        NOT NULL,

    -- auditoría
    creado_por       UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en   TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_actividad_proyecto_fase_proyecto_id ON actividad_proyecto (fase_proyecto_id);
CREATE INDEX IF NOT EXISTS idx_actividad_proyecto_creado_por       ON actividad_proyecto (creado_por);


-- Actividades de aprendizaje dentro de una actividad de proyecto.
CREATE TABLE IF NOT EXISTS actividad_aprendizaje (
    -- identidad
    id                    UUID        PRIMARY KEY,

    -- padre
    actividad_proyecto_id UUID        NOT NULL REFERENCES actividad_proyecto(id) ON DELETE CASCADE,

    -- visualización
    nombre                TEXT        NOT NULL,
    descripcion           TEXT,

    -- programación
    fecha_inicio          DATE,
    fecha_fin             DATE,
    orden                 INTEGER     NOT NULL DEFAULT 0,

    -- auditoría
    creado_por            UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en        TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_actividad_aprendizaje_actividad_proyecto_id ON actividad_aprendizaje (actividad_proyecto_id);
CREATE INDEX IF NOT EXISTS idx_actividad_aprendizaje_creado_por            ON actividad_aprendizaje (creado_por);


-- Guía de aprendizaje adjunta a una actividad (relación 1:1).
CREATE TABLE IF NOT EXISTS guia_aprendizaje (
    -- identidad
    id                       UUID        PRIMARY KEY,

    -- padre (1:1)
    actividad_aprendizaje_id UUID        NOT NULL UNIQUE
                                 REFERENCES actividad_aprendizaje(id) ON DELETE CASCADE,

    -- contenido
    url                      TEXT        NOT NULL,
    subido_en                TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- auditoría
    creado_por               UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en           TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_guia_aprendizaje_actividad_aprendizaje_id ON guia_aprendizaje (actividad_aprendizaje_id);
CREATE INDEX IF NOT EXISTS idx_guia_aprendizaje_creado_por               ON guia_aprendizaje (creado_por);


-- Evidencia de aprendizaje asociada a una actividad (relación 1:1).
CREATE TABLE IF NOT EXISTS evidencia_aprendizaje (
    -- identidad
    id                       UUID        PRIMARY KEY,

    -- padre (1:1)
    actividad_aprendizaje_id UUID        NOT NULL UNIQUE
                                 REFERENCES actividad_aprendizaje(id) ON DELETE CASCADE,

    -- visualización
    descripcion              TEXT,

    -- auditoría
    creado_por               UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en           TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_evidencia_aprendizaje_actividad_aprendizaje_id ON evidencia_aprendizaje (actividad_aprendizaje_id);
CREATE INDEX IF NOT EXISTS idx_evidencia_aprendizaje_creado_por               ON evidencia_aprendizaje (creado_por);


-- Entrega de evidencia por un aprendiz, con calificación del instructor.
-- usuario_id (aprendiz): RESTRICT — no se borra un usuario con entregas.
CREATE TABLE IF NOT EXISTS entrega_evidencia (
    -- identidad
    id                       UUID        PRIMARY KEY,

    -- vínculos
    evidencia_aprendizaje_id UUID        NOT NULL
                                 REFERENCES evidencia_aprendizaje(id) ON DELETE CASCADE,
    usuario_id               UUID        NOT NULL REFERENCES usuario(id) ON DELETE RESTRICT,

    -- entrega
    url                      TEXT,
    entregado_en             TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- calificación
    calificacion             NUMERIC(5,2),
    observaciones            TEXT,
    retroalimentacion        TEXT,
    aprueba                  BOOLEAN,
    calificado_en            TIMESTAMPTZ DEFAULT NULL,

    -- auditoría
    creado_por               UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en           TIMESTAMPTZ DEFAULT NULL,

    UNIQUE (evidencia_aprendizaje_id, usuario_id)
);

CREATE INDEX IF NOT EXISTS idx_entrega_evidencia_evidencia_aprendizaje_id ON entrega_evidencia (evidencia_aprendizaje_id);
CREATE INDEX IF NOT EXISTS idx_entrega_evidencia_usuario_id               ON entrega_evidencia (usuario_id);
CREATE INDEX IF NOT EXISTS idx_entrega_evidencia_creado_por               ON entrega_evidencia (creado_por);


-- Secciones dentro de una actividad de aprendizaje.
CREATE TABLE IF NOT EXISTS seccion_actividad (
    -- identidad
    id                       UUID        PRIMARY KEY,

    -- padre
    actividad_aprendizaje_id UUID        NOT NULL
                                 REFERENCES actividad_aprendizaje(id) ON DELETE CASCADE,

    -- visualización
    nombre                   TEXT        NOT NULL,
    descripcion              TEXT,

    -- contenido
    archivo_url              TEXT,
    archivo_tipo             TEXT,

    -- programación
    fecha_inicio             DATE,
    fecha_fin                DATE,
    orden                    INTEGER     NOT NULL DEFAULT 0,

    -- auditoría
    creado_por               UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en           TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_seccion_actividad_actividad_aprendizaje_id ON seccion_actividad (actividad_aprendizaje_id);
CREATE INDEX IF NOT EXISTS idx_seccion_actividad_creado_por               ON seccion_actividad (creado_por);


-- Subsecciones dentro de una sección de actividad.
CREATE TABLE IF NOT EXISTS sub_seccion_actividad (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- padre
    seccion_id     UUID        NOT NULL REFERENCES seccion_actividad(id) ON DELETE CASCADE,

    -- visualización
    nombre         TEXT        NOT NULL,
    descripcion    TEXT,

    -- contenido
    archivo_url    TEXT,
    archivo_tipo   TEXT,

    -- programación
    fecha_inicio   DATE,
    fecha_fin      DATE,
    orden          INTEGER     NOT NULL DEFAULT 0,

    -- auditoría
    creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_sub_seccion_actividad_seccion_id ON sub_seccion_actividad (seccion_id);
CREATE INDEX IF NOT EXISTS idx_sub_seccion_actividad_creado_por ON sub_seccion_actividad (creado_por);


-- Guías adjuntas a una actividad de proyecto (uso del instructor).
CREATE TABLE IF NOT EXISTS guia_actividad_proyecto (
    -- identidad
    id                    UUID        PRIMARY KEY,

    -- padre
    actividad_proyecto_id UUID        NOT NULL
                              REFERENCES actividad_proyecto(id) ON DELETE CASCADE,

    -- visualización y contenido
    nombre                TEXT,
    descripcion           TEXT,
    url                   TEXT        NOT NULL,
    orden                 INTEGER     NOT NULL DEFAULT 0,
    subido_en             TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- auditoría
    creado_por            UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en        TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_guia_actividad_proyecto_actividad_proyecto_id ON guia_actividad_proyecto (actividad_proyecto_id);
CREATE INDEX IF NOT EXISTS idx_guia_actividad_proyecto_creado_por            ON guia_actividad_proyecto (creado_por);

-- ============================================================
-- PROGRAMAS Y FICHAS
-- ============================================================

-- Programa de formación: combinación de área y nivel.
CREATE TABLE IF NOT EXISTS programa_formacion (
    -- identidad
    id                  UUID        PRIMARY KEY,

    -- padres
    area_id             UUID        NOT NULL REFERENCES area(id)            ON DELETE RESTRICT,
    nivel_formacion_id  UUID        NOT NULL REFERENCES nivel_formacion(id) ON DELETE RESTRICT,

    -- visualización
    nombre              TEXT        NOT NULL,

    -- auditoría
    creado_por          UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en      TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_programa_formacion_area_id            ON programa_formacion (area_id);
CREATE INDEX IF NOT EXISTS idx_programa_formacion_nivel_formacion_id ON programa_formacion (nivel_formacion_id);
CREATE INDEX IF NOT EXISTS idx_programa_formacion_creado_por         ON programa_formacion (creado_por);


-- Ficha de formación: cohorte de aprendices en un programa.
CREATE TABLE IF NOT EXISTS ficha_formacion (
    -- identidad
    id                    UUID        PRIMARY KEY,
    numero                TEXT        COLLATE "C" NOT NULL UNIQUE,

    -- padres
    programa_formacion_id UUID        NOT NULL REFERENCES programa_formacion(id) ON DELETE RESTRICT,
    coordinacion_id       UUID        NOT NULL REFERENCES coordinacion(id)       ON DELETE RESTRICT,

    -- vínculos opcionales
    proyecto_formativo_id UUID        REFERENCES proyecto_formativo(id) ON DELETE SET NULL,
    instructor_id         UUID        REFERENCES instructor(id)         ON DELETE SET NULL,

    -- auditoría
    creado_por            UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en        TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_ficha_formacion_programa_formacion_id ON ficha_formacion (programa_formacion_id);
CREATE INDEX IF NOT EXISTS idx_ficha_formacion_coordinacion_id       ON ficha_formacion (coordinacion_id);
CREATE INDEX IF NOT EXISTS idx_ficha_formacion_proyecto_formativo_id ON ficha_formacion (proyecto_formativo_id);
CREATE INDEX IF NOT EXISTS idx_ficha_formacion_instructor_id         ON ficha_formacion (instructor_id);
CREATE INDEX IF NOT EXISTS idx_ficha_formacion_creado_por            ON ficha_formacion (creado_por);


-- Instructores asignados a una ficha (competencias).
CREATE TABLE IF NOT EXISTS ficha_instructor_competencia (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- vínculos
    ficha_id       UUID        NOT NULL REFERENCES ficha_formacion(id) ON DELETE CASCADE,
    instructor_id  UUID        NOT NULL REFERENCES instructor(id)      ON DELETE CASCADE,

    -- auditoría
    creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL,

    UNIQUE (ficha_id, instructor_id)
);

CREATE INDEX IF NOT EXISTS idx_ficha_instructor_competencia_ficha_id      ON ficha_instructor_competencia (ficha_id);
CREATE INDEX IF NOT EXISTS idx_ficha_instructor_competencia_instructor_id ON ficha_instructor_competencia (instructor_id);
CREATE INDEX IF NOT EXISTS idx_ficha_instructor_competencia_creado_por    ON ficha_instructor_competencia (creado_por);


-- Asistencia de aprendices por ficha y fecha.
CREATE TABLE IF NOT EXISTS asistencia_aprendiz (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- vínculos
    ficha_id       UUID        NOT NULL REFERENCES ficha_formacion(id) ON DELETE CASCADE,
    aprendiz_id    UUID        NOT NULL REFERENCES aprendiz(id)        ON DELETE CASCADE,

    -- datos
    fecha          DATE        NOT NULL,
    estado         TEXT        NOT NULL DEFAULT 'Presente',

    -- auditoría
    creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL,

    UNIQUE (ficha_id, aprendiz_id, fecha)
);

CREATE INDEX IF NOT EXISTS idx_asistencia_aprendiz_ficha_id    ON asistencia_aprendiz (ficha_id);
CREATE INDEX IF NOT EXISTS idx_asistencia_aprendiz_aprendiz_id ON asistencia_aprendiz (aprendiz_id);
CREATE INDEX IF NOT EXISTS idx_asistencia_aprendiz_creado_por  ON asistencia_aprendiz (creado_por);

-- ============================================================
-- EXTRAS DEL APRENDIZ
-- ============================================================

-- Fases del proceso formativo SENA (catálogo independiente).
-- Distinto de fase_proyecto: este es el catálogo general de fases.
CREATE TABLE IF NOT EXISTS fase (
    -- identidad
    id             UUID         PRIMARY KEY,

    -- visualización
    nombre         VARCHAR(150) NOT NULL UNIQUE,
    descripcion    TEXT,

    -- orden
    orden          SMALLINT     NOT NULL DEFAULT 1,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ  DEFAULT NULL
);


-- Notificaciones para cualquier usuario del sistema.
CREATE TABLE IF NOT EXISTS notificacion (
    -- identidad
    id             UUID        PRIMARY KEY,

    -- propietario
    usuario_id     UUID        NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,

    -- contenido
    mensaje        TEXT        NOT NULL,
    tipo           VARCHAR(10) NOT NULL DEFAULT 'info'
                       CHECK (tipo IN ('info', 'success', 'warning', 'danger')),
    url_destino    TEXT,

    -- estado
    leida          BOOLEAN     NOT NULL DEFAULT FALSE,

    -- auditoría
    creado_por     UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_notificacion_usuario_id ON notificacion (usuario_id);
CREATE INDEX IF NOT EXISTS idx_notificacion_creado_por ON notificacion (creado_por);

COMMIT;
