-- migrate:up

-- ============================================================
-- Reemplaza los 4 booleanos de etapa en ficha_aprendiz por un
-- ENUM que soporta estados SENA (trasladado, suspendido, etc.)
-- ============================================================

-- 1. Tipo ENUM
CREATE TYPE estado_formacion_aprendiz AS ENUM (
    'lectiva_en_curso',
    'lectiva_concluida',
    'productiva_en_curso',
    'productiva_concluida',
    'trasladado',
    'suspendido'
);

-- 2. Nueva columna (nullable para poder migrar datos primero)
ALTER TABLE ficha_aprendiz ADD COLUMN estado estado_formacion_aprendiz;

-- 3. Mapeo de booleanos al ENUM
UPDATE ficha_aprendiz SET estado =
    CASE
        WHEN en_etapa_productiva = TRUE AND etapa_productiva_concluida = TRUE
            THEN 'productiva_concluida'
        WHEN en_etapa_productiva = TRUE
            THEN 'productiva_en_curso'
        WHEN etapa_lectiva_concluida = TRUE
            THEN 'lectiva_concluida'
        ELSE 'lectiva_en_curso'
    END::estado_formacion_aprendiz;

-- 4. Aplicar NOT NULL y default
ALTER TABLE ficha_aprendiz ALTER COLUMN estado SET NOT NULL;
ALTER TABLE ficha_aprendiz ALTER COLUMN estado SET DEFAULT 'lectiva_en_curso';

-- 5. Eliminar constraints CHECK que dependian de los booleanos
ALTER TABLE ficha_aprendiz
    DROP CONSTRAINT IF EXISTS ficha_aprendiz_check,
    DROP CONSTRAINT IF EXISTS ficha_aprendiz_check1;

-- 6. Eliminar columnas booleanas obsoletas
ALTER TABLE ficha_aprendiz
    DROP COLUMN en_etapa_lectiva,
    DROP COLUMN etapa_lectiva_concluida,
    DROP COLUMN en_etapa_productiva,
    DROP COLUMN etapa_productiva_concluida;


-- migrate:down

ALTER TABLE ficha_aprendiz
    ADD COLUMN en_etapa_lectiva            BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN etapa_lectiva_concluida     BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN en_etapa_productiva         BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN etapa_productiva_concluida  BOOLEAN NOT NULL DEFAULT FALSE;

UPDATE ficha_aprendiz SET
    en_etapa_lectiva           = (estado = 'lectiva_en_curso'),
    etapa_lectiva_concluida    = (estado IN ('lectiva_concluida', 'productiva_en_curso', 'productiva_concluida')),
    en_etapa_productiva        = (estado IN ('productiva_en_curso', 'productiva_concluida')),
    etapa_productiva_concluida = (estado = 'productiva_concluida');

ALTER TABLE ficha_aprendiz
    ADD CONSTRAINT ficha_aprendiz_check  CHECK (en_etapa_productiva = FALSE OR etapa_lectiva_concluida = TRUE),
    ADD CONSTRAINT ficha_aprendiz_check1 CHECK (etapa_productiva_concluida = FALSE OR en_etapa_productiva = TRUE);

ALTER TABLE ficha_aprendiz DROP COLUMN estado;

DROP TYPE estado_formacion_aprendiz;
