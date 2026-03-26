-- migrate:up

-- Remove empresa assignment fields from ficha_aprendiz.
-- Company linkage now lives in contrato_aprendizaje.
ALTER TABLE ficha_aprendiz DROP COLUMN IF EXISTS empresa_id;
ALTER TABLE ficha_aprendiz DROP COLUMN IF EXISTS fecha_inicio_ep;
ALTER TABLE ficha_aprendiz DROP COLUMN IF EXISTS fecha_fin_ep;

-- Drop the index that referenced empresa_id (may not exist on all envs).
DROP INDEX IF EXISTS idx_ficha_aprendiz_empresa_id;


-- migrate:down

ALTER TABLE ficha_aprendiz
    ADD COLUMN IF NOT EXISTS empresa_id      UUID REFERENCES empresa(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS fecha_inicio_ep DATE,
    ADD COLUMN IF NOT EXISTS fecha_fin_ep    DATE;

CREATE INDEX IF NOT EXISTS idx_ficha_aprendiz_empresa_id
    ON ficha_aprendiz (empresa_id);
