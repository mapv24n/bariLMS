-- migrate:up

-- Adds missing UNIQUE constraints on `nombre` for tables used by seed
-- scripts with ON CONFLICT (nombre) DO NOTHING.

ALTER TABLE centro
    ADD CONSTRAINT centro_nombre_unique UNIQUE (nombre);

ALTER TABLE coordinacion
    ADD CONSTRAINT coordinacion_nombre_unique UNIQUE (nombre);

ALTER TABLE area
    ADD CONSTRAINT area_nombre_unique UNIQUE (nombre);

ALTER TABLE programa_formacion
    ADD CONSTRAINT programa_formacion_nombre_unique UNIQUE (nombre);


-- migrate:down

ALTER TABLE programa_formacion DROP CONSTRAINT IF EXISTS programa_formacion_nombre_unique;
ALTER TABLE area               DROP CONSTRAINT IF EXISTS area_nombre_unique;
ALTER TABLE coordinacion       DROP CONSTRAINT IF EXISTS coordinacion_nombre_unique;
ALTER TABLE centro             DROP CONSTRAINT IF EXISTS centro_nombre_unique;
