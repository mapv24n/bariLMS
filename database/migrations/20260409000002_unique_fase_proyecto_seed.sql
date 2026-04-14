-- migrate:up

-- Prevents duplicate fase_proyecto rows on repeated seed runs.
-- Seeds use ON CONFLICT (nombre, proyecto_formativo_id) DO NOTHING.

ALTER TABLE fase_proyecto
    ADD CONSTRAINT fase_proyecto_nombre_proyecto_unique UNIQUE (nombre, proyecto_formativo_id);


-- migrate:down

ALTER TABLE fase_proyecto DROP CONSTRAINT IF EXISTS fase_proyecto_nombre_proyecto_unique;
