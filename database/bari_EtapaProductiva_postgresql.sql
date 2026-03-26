-- ============================================================
-- Proyecto    : bariLMS — Módulo Etapa Productiva
-- Archivo     : database/bari_EtapaProductiva_postgresql.sql
-- Descripción : Esquema del módulo de Etapa Productiva.
--               Depende de bari_lms_postgresql.sql (debe ejecutarse primero).
--
-- Cómo aplicar:
--   1. psql -U <usuario> -d <base> -f database/bari_lms_postgresql.sql
--   2. psql -U <usuario> -d <base> -f database/bari_EtapaProductiva_postgresql.sql
--
-- Diseño:
--   Un aprendiz atraviesa dos etapas en su proceso formativo:
--     Lectiva    → formación presencial en el SENA.
--     Productiva → práctica en empresa.
--
--   Separación de responsabilidades:
--
--   ficha_aprendiz     — Inscripción académica del aprendiz en una ficha.
--                        Registra ÚNICAMENTE el estado formativo de cada etapa
--                        (lectiva y productiva). No contiene datos de empresa.
--
--   empresa            — Catálogo de empresas que vinculan aprendices en EP.
--
--   contrato_aprendizaje — Vínculo productivo: relaciona al aprendiz
--                          (dentro del contexto de su ficha) con una empresa.
--                          Tiene vida propia: fechas, estado, observaciones.
--                          Un aprendiz puede tener múltiples contratos a lo
--                          largo de su etapa productiva (cambio de empresa,
--                          cancelación, etc.).
--
-- Relación con tablas existentes:
--   aprendiz.ficha TEXT → campo legado; la referencia canónica es
--                         ficha_aprendiz.ficha_id.
-- ============================================================

BEGIN;

-- ============================================================
-- EMPRESA
-- ============================================================

-- Catálogo de empresas o entidades que vinculan aprendices en EP.
-- El NIT se almacena en minúsculas / sin separadores (COLLATE "C").
CREATE TABLE IF NOT EXISTS empresa (
    -- identidad
    id              UUID        PRIMARY KEY,

    -- datos legales
    razon_social    TEXT        NOT NULL,
    nit             TEXT        COLLATE "C" NOT NULL UNIQUE,

    -- clasificación
    sector          TEXT,

    -- contacto
    correo          TEXT        COLLATE "C",
    telefono        TEXT,
    direccion       TEXT,

    -- estado
    activo          BOOLEAN     NOT NULL DEFAULT TRUE,

    -- auditoría
    creado_por      UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ DEFAULT NULL,

    CHECK (correo IS NULL OR correo = lower(correo)),
    CHECK (nit    = lower(nit))
);

CREATE INDEX IF NOT EXISTS idx_empresa_nit        ON empresa (nit);
CREATE INDEX IF NOT EXISTS idx_empresa_creado_por ON empresa (creado_por);


-- ============================================================
-- INSCRIPCIÓN APRENDIZ ↔ FICHA  (reemplaza aprendiz.ficha TEXT)
-- ============================================================

-- Inscripción académica de un aprendiz en una ficha de formación.
-- Registra ÚNICAMENTE el estado formativo de ambas etapas.
-- La asignación de empresa vive en contrato_aprendizaje.
--
-- Etapa Lectiva:
--   en_etapa_lectiva         TRUE  mientras el aprendiz cursa la formación presencial.
--   etapa_lectiva_concluida  TRUE  cuando aprueba todas las competencias de la ficha.
--                                  Requisito para habilitar la etapa productiva.
--
-- Etapa Productiva:
--   en_etapa_productiva         TRUE  una vez que se habilita al aprendiz para EP.
--   etapa_productiva_concluida  TRUE  al finalizar formalmente su etapa productiva.
--
-- Reglas de negocio (validadas en la capa de aplicación):
--   • en_etapa_productiva solo puede ser TRUE si etapa_lectiva_concluida = TRUE.
--   • etapa_productiva_concluida solo puede ser TRUE si en_etapa_productiva = TRUE.
CREATE TABLE IF NOT EXISTS ficha_aprendiz (
    -- identidad
    id                          UUID        PRIMARY KEY,

    -- inscripción
    ficha_id                    UUID        NOT NULL REFERENCES ficha_formacion(id) ON DELETE RESTRICT,
    aprendiz_id                 UUID        NOT NULL REFERENCES aprendiz(id)        ON DELETE RESTRICT,

    -- ── Etapa Lectiva ─────────────────────────────────────────
    en_etapa_lectiva            BOOLEAN     NOT NULL DEFAULT TRUE,
    etapa_lectiva_concluida     BOOLEAN     NOT NULL DEFAULT FALSE,

    -- ── Etapa Productiva ──────────────────────────────────────
    en_etapa_productiva         BOOLEAN     NOT NULL DEFAULT FALSE,
    etapa_productiva_concluida  BOOLEAN     NOT NULL DEFAULT FALSE,

    -- auditoría
    creado_por                  UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en                   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en              TIMESTAMPTZ DEFAULT NULL,

    -- un aprendiz se inscribe una sola vez por ficha
    UNIQUE (ficha_id, aprendiz_id),

    -- integridad de fases: no puede estar en EP sin haber concluido lectiva
    CHECK (
        en_etapa_productiva = FALSE
        OR etapa_lectiva_concluida = TRUE
    ),
    -- no puede concluir EP sin estar en EP
    CHECK (
        etapa_productiva_concluida = FALSE
        OR en_etapa_productiva = TRUE
    )
);

CREATE INDEX IF NOT EXISTS idx_ficha_aprendiz_ficha_id    ON ficha_aprendiz (ficha_id);
CREATE INDEX IF NOT EXISTS idx_ficha_aprendiz_aprendiz_id ON ficha_aprendiz (aprendiz_id);
CREATE INDEX IF NOT EXISTS idx_ficha_aprendiz_creado_por  ON ficha_aprendiz (creado_por);

-- Índice parcial: búsqueda rápida de aprendices habilitados en EP por ficha.
CREATE INDEX IF NOT EXISTS idx_ficha_aprendiz_ep_activa
    ON ficha_aprendiz (ficha_id)
    WHERE en_etapa_productiva = TRUE;


-- ============================================================
-- CONTRATO DE APRENDIZAJE
-- ============================================================

-- Vínculo productivo entre un aprendiz (en el contexto de su ficha)
-- y una empresa. Tiene vida propia: fechas, estado y observaciones.
--
-- Se usa ficha_aprendiz_id (no ficha_id + aprendiz_id por separado)
-- porque la relación siempre ocurre dentro de una inscripción concreta:
-- el mismo aprendiz en fichas distintas puede tener contratos distintos.
--
-- Un aprendiz puede acumular varios registros a lo largo de su EP:
-- cambio de empresa, cancelación y reasignación, etc.
-- El contrato vigente es el que tiene estado = 'activo'.
CREATE TABLE IF NOT EXISTS contrato_aprendizaje (
    -- identidad
    id                  UUID        PRIMARY KEY,

    -- contexto educativo
    ficha_aprendiz_id   UUID        NOT NULL REFERENCES ficha_aprendiz(id) ON DELETE RESTRICT,

    -- empresa vinculante
    empresa_id          UUID        NOT NULL REFERENCES empresa(id)        ON DELETE RESTRICT,

    -- vigencia
    fecha_inicio        DATE,
    fecha_fin           DATE,

    -- estado del contrato
    estado              TEXT        NOT NULL DEFAULT 'activo'
                        CHECK (estado IN ('activo', 'terminado', 'cancelado')),

    -- notas adicionales
    observaciones       TEXT,

    -- auditoría
    creado_por          UUID        REFERENCES usuario(id) ON DELETE SET NULL,

    -- marcas de tiempo
    creado_en           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en      TIMESTAMPTZ DEFAULT NULL,

    CHECK (fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio)
);

CREATE INDEX IF NOT EXISTS idx_contrato_ficha_aprendiz ON contrato_aprendizaje (ficha_aprendiz_id);
CREATE INDEX IF NOT EXISTS idx_contrato_empresa        ON contrato_aprendizaje (empresa_id);
CREATE INDEX IF NOT EXISTS idx_contrato_estado         ON contrato_aprendizaje (estado);

-- Índice parcial: contratos activos (consulta más frecuente).
CREATE INDEX IF NOT EXISTS idx_contrato_activo
    ON contrato_aprendizaje (ficha_aprendiz_id)
    WHERE estado = 'activo';

COMMIT;
