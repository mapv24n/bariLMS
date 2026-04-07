-- migrate:up

-- ============================================================
-- EP_FACTOR — catálogo global de factores de evaluación EP.
-- Tipo: tecnico | actitudinal.
-- La columna `orden` controla el orden de visualización dentro
-- de cada tipo.
-- ============================================================
CREATE TABLE IF NOT EXISTS ep_factor (
    id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo  TEXT NOT NULL,
    nombre  TEXT NOT NULL,
    tipo    TEXT NOT NULL CHECK (tipo IN ('tecnico', 'actitudinal')),
    orden   INT  NOT NULL DEFAULT 0,

    UNIQUE (codigo)
);

-- Factores estándar SENA (se insertan una sola vez gracias a ON CONFLICT).
INSERT INTO ep_factor (codigo, nombre, tipo, orden) VALUES
    ('aplicacion_conocimiento',     'Aplicación de conocimiento',           'tecnico',      1),
    ('mejora_continua',             'Mejora continua',                      'tecnico',      2),
    ('fortalecimiento_ocupacional', 'Fortalecimiento ocupacional',           'tecnico',      3),
    ('oportunidad_calidad',         'Oportunidad y calidad',                'tecnico',      4),
    ('responsabilidad_ambiental',   'Responsabilidad ambiental',            'tecnico',      5),
    ('administracion_recursos',     'Administración de recursos',           'tecnico',      6),
    ('sst',                         'Seguridad y salud en el trabajo',      'tecnico',      7),
    ('documentacion_ep',            'Documentación etapa productiva',       'tecnico',      8),
    ('relaciones_interpersonales',  'Relaciones interpersonales',           'actitudinal',  1),
    ('trabajo_equipo',              'Trabajo en equipo',                    'actitudinal',  2),
    ('solucion_problemas',          'Solución de problemas',                'actitudinal',  3),
    ('cumplimiento',                'Cumplimiento',                         'actitudinal',  4),
    ('organizacion',                'Organización',                         'actitudinal',  5)
ON CONFLICT (codigo) DO NOTHING;


-- ============================================================
-- EP_FACTOR_PROYECTO — personalización de factores por proyecto.
-- Si un proyecto_formativo no tiene filas aquí, se usan TODOS
-- los factores del catálogo.  Si tiene filas, solo se usan esos.
-- ============================================================
CREATE TABLE IF NOT EXISTS ep_factor_proyecto (
    factor_id              UUID NOT NULL REFERENCES ep_factor(id)            ON DELETE CASCADE,
    proyecto_formativo_id  UUID NOT NULL REFERENCES proyecto_formativo(id)   ON DELETE CASCADE,

    PRIMARY KEY (factor_id, proyecto_formativo_id)
);

CREATE INDEX IF NOT EXISTS idx_ep_factor_proyecto_proyecto
    ON ep_factor_proyecto (proyecto_formativo_id);


-- ============================================================
-- PROCESO_EP — registro principal del proceso de seguimiento.
-- Uno por contrato activo.
-- ============================================================
CREATE TABLE IF NOT EXISTS proceso_ep (
    id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    contrato_id    UUID        NOT NULL REFERENCES contrato_aprendizaje(id) ON DELETE RESTRICT,
    instructor_id  UUID        NOT NULL REFERENCES instructor(id)           ON DELETE RESTRICT,
    estado         TEXT        NOT NULL DEFAULT 'activo'
                               CHECK (estado IN ('activo', 'completado', 'cancelado')),
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL,

    UNIQUE (contrato_id)
);

CREATE INDEX IF NOT EXISTS idx_proceso_ep_contrato   ON proceso_ep (contrato_id);
CREATE INDEX IF NOT EXISTS idx_proceso_ep_instructor ON proceso_ep (instructor_id);


-- ============================================================
-- EP_MOMENTO_1 — Planeación (uno por proceso).
-- No tiene factores evaluados; eso ocurre desde el momento 2.
-- ============================================================
CREATE TABLE IF NOT EXISTS ep_momento_1 (
    id                     UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    proceso_id             UUID        NOT NULL REFERENCES proceso_ep(id) ON DELETE CASCADE,

    fecha_inicio_ep        DATE,
    fecha_fin_ep           DATE,
    arl_fecha_afiliacion   DATE,
    arl_poliza_numero      TEXT,
    jornada                TEXT,
    dias_semana            TEXT,
    hora                   TEXT,
    url_grabacion          TEXT,

    competencias           TEXT,
    resultados_aprendizaje TEXT,
    actividades            TEXT,
    evidencias             TEXT,
    observaciones          TEXT,

    firma_aprendiz         BOOLEAN     NOT NULL DEFAULT FALSE,
    firma_instructor       BOOLEAN     NOT NULL DEFAULT FALSE,
    firma_coformador       BOOLEAN     NOT NULL DEFAULT FALSE,
    ciudad                 TEXT,
    fecha_firma            DATE,
    modalidad_firma        TEXT,

    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL,

    UNIQUE (proceso_id)
);

CREATE INDEX IF NOT EXISTS idx_ep_m1_proceso ON ep_momento_1 (proceso_id);


-- ============================================================
-- EP_MOMENTO_2 — Seguimiento (uno por proceso).
-- Los factores evaluados viven en ep_momento_2_evaluacion.
-- ============================================================
CREATE TABLE IF NOT EXISTS ep_momento_2 (
    id                     UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    proceso_id             UUID        NOT NULL REFERENCES proceso_ep(id) ON DELETE CASCADE,

    fecha_inicio_ep        DATE,
    fecha_momento          DATE,
    modalidad_seguimiento  TEXT,
    url_grabacion          TEXT,

    obs_instructor         TEXT,
    obs_aprendiz           TEXT,
    obs_coformador         TEXT,

    firma_aprendiz         BOOLEAN     NOT NULL DEFAULT FALSE,
    firma_instructor       BOOLEAN     NOT NULL DEFAULT FALSE,
    firma_coformador       BOOLEAN     NOT NULL DEFAULT FALSE,
    ciudad                 TEXT,
    fecha_firma            DATE,
    modalidad_firma        TEXT,

    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL,

    UNIQUE (proceso_id)
);

CREATE INDEX IF NOT EXISTS idx_ep_m2_proceso ON ep_momento_2 (proceso_id);


-- ============================================================
-- EP_MOMENTO_2_EVALUACION — un fila por (seguimiento, factor).
-- Vincula el resultado de la evaluación de un factor al momento 2.
-- ============================================================
CREATE TABLE IF NOT EXISTS ep_momento_2_evaluacion (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    momento_id    UUID NOT NULL REFERENCES ep_momento_2(id) ON DELETE CASCADE,
    factor_id     UUID NOT NULL REFERENCES ep_factor(id)    ON DELETE RESTRICT,
    valoracion    TEXT,
    observaciones TEXT,

    UNIQUE (momento_id, factor_id)
);

CREATE INDEX IF NOT EXISTS idx_ep_m2_eval_momento ON ep_momento_2_evaluacion (momento_id);
CREATE INDEX IF NOT EXISTS idx_ep_m2_eval_factor  ON ep_momento_2_evaluacion (factor_id);


-- ============================================================
-- EP_MOMENTO_3 — Evaluación final (uno por proceso).
-- Los factores evaluados viven en ep_momento_3_evaluacion.
-- ============================================================
CREATE TABLE IF NOT EXISTS ep_momento_3 (
    id                        UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    proceso_id                UUID    NOT NULL REFERENCES proceso_ep(id) ON DELETE CASCADE,

    fecha_inicio_ep           DATE,
    fecha_fin_ep              DATE,
    num_visitas               INT,
    modalidad_evaluacion      TEXT,
    url_grabacion             TEXT,

    retro_proceso_coformador  TEXT,
    retro_desempeno_coformador TEXT,
    retro_proceso_instructor  TEXT,
    retro_desempeno_instructor TEXT,
    retro_proceso_aprendiz    TEXT,
    retro_desempeno_aprendiz  TEXT,

    juicio_resultado          TEXT    CHECK (juicio_resultado IN ('Aprobado', 'No aprobado')),
    juicio_observaciones      TEXT,

    firma_aprendiz            BOOLEAN NOT NULL DEFAULT FALSE,
    firma_instructor          BOOLEAN NOT NULL DEFAULT FALSE,
    firma_coformador          BOOLEAN NOT NULL DEFAULT FALSE,
    ciudad                    TEXT,
    fecha_firma               DATE,
    modalidad_firma           TEXT,

    creado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NULL,

    UNIQUE (proceso_id)
);

CREATE INDEX IF NOT EXISTS idx_ep_m3_proceso ON ep_momento_3 (proceso_id);


-- ============================================================
-- EP_MOMENTO_3_EVALUACION — misma estructura que la del momento 2.
-- ============================================================
CREATE TABLE IF NOT EXISTS ep_momento_3_evaluacion (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    momento_id    UUID NOT NULL REFERENCES ep_momento_3(id) ON DELETE CASCADE,
    factor_id     UUID NOT NULL REFERENCES ep_factor(id)    ON DELETE RESTRICT,
    valoracion    TEXT,
    observaciones TEXT,

    UNIQUE (momento_id, factor_id)
);

CREATE INDEX IF NOT EXISTS idx_ep_m3_eval_momento ON ep_momento_3_evaluacion (momento_id);
CREATE INDEX IF NOT EXISTS idx_ep_m3_eval_factor  ON ep_momento_3_evaluacion (factor_id);


-- migrate:down

DROP TABLE IF EXISTS ep_momento_3_evaluacion;
DROP TABLE IF EXISTS ep_momento_3;
DROP TABLE IF EXISTS ep_momento_2_evaluacion;
DROP TABLE IF EXISTS ep_momento_2;
DROP TABLE IF EXISTS ep_momento_1;
DROP TABLE IF EXISTS proceso_ep;
DROP TABLE IF EXISTS ep_factor_proyecto;
DROP TABLE IF EXISTS ep_factor;
