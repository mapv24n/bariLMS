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
--   El aprendiz es la MISMA entidad en ambas etapas. No se crea
--   una entidad separada para EP. El estado de cada etapa se
--   registra en ficha_aprendiz, que representa la inscripción
--   oficial del aprendiz en una ficha de formación.
--
--   Esto preserva la tabla aprendiz intacta (sin columnas nuevas)
--   y no rompe ninguna consulta existente.
--
--   Tablas:
--     empresa        — Empresas que vinculan aprendices en EP.
--     ficha_aprendiz — Inscripción del aprendiz en una ficha.
--                      Registra el estado de la etapa lectiva y
--                      de la etapa productiva para ese aprendiz.
--
-- Relación con tablas existentes:
--   asistencia_aprendiz → control de asistencia diaria (sin cambios).
--   ficha_aprendiz      → inscripción + estado de fase (este archivo).
--   aprendiz.ficha TEXT → campo legado; la referencia canónica es
--                         ficha_aprendiz.ficha_id.
-- ============================================================

BEGIN;

-- ============================================================
-- EMPRESA
-- ============================================================

-- Empresa o entidad que vincula aprendices en etapa productiva.
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

-- Inscripción oficial de un aprendiz en una ficha de formación.
-- Registra el estado de ambas etapas del proceso formativo SENA.
--
-- Etapa Lectiva:
--   en_etapa_lectiva         TRUE  mientras el aprendiz cursa la formación presencial.
--   etapa_lectiva_concluida  TRUE  cuando aprueba todas las competencias de la ficha.
--                                  Requisito para habilitar la etapa productiva.
--
-- Etapa Productiva:
--   en_etapa_productiva         TRUE  una vez habilitado e iniciada la práctica en empresa.
--   etapa_productiva_concluida  TRUE  al finalizar el contrato de aprendizaje.
--
-- Reglas de negocio (validadas en la capa de aplicación):
--   • en_etapa_productiva solo puede ser TRUE si etapa_lectiva_concluida = TRUE.
--   • etapa_productiva_concluida solo puede ser TRUE si en_etapa_productiva = TRUE.
--   • Un aprendiz aparece en el módulo EP del instructor únicamente si
--     en_etapa_productiva = TRUE para la ficha consultada.
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

    -- empresa asignada (NULL hasta que se formalice el contrato)
    empresa_id                  UUID        REFERENCES empresa(id) ON DELETE SET NULL,

    -- fechas del contrato de aprendizaje (NULL mientras no haya contrato)
    fecha_inicio_ep             DATE,
    fecha_fin_ep                DATE,

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
CREATE INDEX IF NOT EXISTS idx_ficha_aprendiz_empresa_id  ON ficha_aprendiz (empresa_id);
CREATE INDEX IF NOT EXISTS idx_ficha_aprendiz_creado_por  ON ficha_aprendiz (creado_por);

-- Índice parcial: búsqueda rápida de aprendices activos en EP por ficha.
CREATE INDEX IF NOT EXISTS idx_ficha_aprendiz_ep_activa
    ON ficha_aprendiz (ficha_id)
    WHERE en_etapa_productiva = TRUE;

COMMIT;
