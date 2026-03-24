-- migrate:up

-- ============================================================
-- EMPRESA - catalogo de empresas vinculantes
-- ============================================================
CREATE TABLE IF NOT EXISTS empresa (
    id              UUID        PRIMARY KEY,
    razon_social    TEXT        NOT NULL,
    nit             TEXT        COLLATE "C" NOT NULL UNIQUE,
    sector          TEXT,
    correo          TEXT        COLLATE "C",
    telefono        TEXT,
    direccion       TEXT,
    activo          BOOLEAN     NOT NULL DEFAULT TRUE,
    creado_por      UUID        REFERENCES usuario(id) ON DELETE SET NULL,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ DEFAULT NULL,

    CHECK (correo IS NULL OR correo = lower(correo)),
    CHECK (nit    = lower(nit))
);

CREATE INDEX IF NOT EXISTS idx_empresa_nit        ON empresa (nit);
CREATE INDEX IF NOT EXISTS idx_empresa_creado_por ON empresa (creado_por);


-- ============================================================
-- FICHA_APRENDIZ - inscripcion academica (estado formativo unicamente)
-- ============================================================
CREATE TABLE IF NOT EXISTS ficha_aprendiz (
    id                          UUID        PRIMARY KEY,
    ficha_id                    UUID        NOT NULL REFERENCES ficha_formacion(id) ON DELETE RESTRICT,
    aprendiz_id                 UUID        NOT NULL REFERENCES aprendiz(id)        ON DELETE RESTRICT,

    -- Etapa Lectiva
    en_etapa_lectiva            BOOLEAN     NOT NULL DEFAULT TRUE,
    etapa_lectiva_concluida     BOOLEAN     NOT NULL DEFAULT FALSE,

    -- Etapa Productiva (estado, no empresa)
    en_etapa_productiva         BOOLEAN     NOT NULL DEFAULT FALSE,
    etapa_productiva_concluida  BOOLEAN     NOT NULL DEFAULT FALSE,

    creado_por      UUID        REFERENCES usuario(id) ON DELETE SET NULL,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ DEFAULT NULL,

    UNIQUE (ficha_id, aprendiz_id),

    CHECK (
        en_etapa_productiva = FALSE
        OR etapa_lectiva_concluida = TRUE
    ),
    CHECK (
        etapa_productiva_concluida = FALSE
        OR en_etapa_productiva = TRUE
    )
);

CREATE INDEX IF NOT EXISTS idx_ficha_aprendiz_ficha_id    ON ficha_aprendiz (ficha_id);
CREATE INDEX IF NOT EXISTS idx_ficha_aprendiz_aprendiz_id ON ficha_aprendiz (aprendiz_id);
CREATE INDEX IF NOT EXISTS idx_ficha_aprendiz_creado_por  ON ficha_aprendiz (creado_por);
CREATE INDEX IF NOT EXISTS idx_ficha_aprendiz_ep_activa
    ON ficha_aprendiz (ficha_id)
    WHERE en_etapa_productiva = TRUE;


-- ============================================================
-- CONTRATO_APRENDIZAJE - vinculo productivo aprendiz <-> empresa
-- ============================================================
CREATE TABLE IF NOT EXISTS contrato_aprendizaje (
    id                  UUID        PRIMARY KEY,
    ficha_aprendiz_id   UUID        NOT NULL REFERENCES ficha_aprendiz(id) ON DELETE RESTRICT,
    empresa_id          UUID        NOT NULL REFERENCES empresa(id)        ON DELETE RESTRICT,
    fecha_inicio        DATE,
    fecha_fin           DATE,
    estado              TEXT        NOT NULL DEFAULT 'activo'
                        CHECK (estado IN ('activo', 'terminado', 'cancelado')),
    observaciones       TEXT,
    creado_por          UUID        REFERENCES usuario(id) ON DELETE SET NULL,
    creado_en           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en      TIMESTAMPTZ DEFAULT NULL,

    CHECK (fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio)
);

CREATE INDEX IF NOT EXISTS idx_contrato_ficha_aprendiz ON contrato_aprendizaje (ficha_aprendiz_id);
CREATE INDEX IF NOT EXISTS idx_contrato_empresa        ON contrato_aprendizaje (empresa_id);
CREATE INDEX IF NOT EXISTS idx_contrato_estado         ON contrato_aprendizaje (estado);
CREATE INDEX IF NOT EXISTS idx_contrato_activo
    ON contrato_aprendizaje (ficha_aprendiz_id)
    WHERE estado = 'activo';


-- migrate:down

-- Eliminar en orden inverso de dependencias FK.
DROP TABLE IF EXISTS contrato_aprendizaje;
DROP TABLE IF EXISTS ficha_aprendiz;
DROP TABLE IF EXISTS empresa;
