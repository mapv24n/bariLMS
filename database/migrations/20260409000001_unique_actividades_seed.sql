-- migrate:up

-- Prevents duplicate seed entries for activity content tables.
-- Seeds use ON CONFLICT (nombre, ...) DO NOTHING, which requires these constraints.

ALTER TABLE actividad_proyecto
    ADD CONSTRAINT actividad_proyecto_nombre_fase_unique UNIQUE (nombre, fase_proyecto_id);

ALTER TABLE actividad_aprendizaje
    ADD CONSTRAINT actividad_aprendizaje_nombre_ap_unique UNIQUE (nombre, actividad_proyecto_id);

ALTER TABLE seccion_actividad
    ADD CONSTRAINT seccion_actividad_nombre_aa_unique UNIQUE (nombre, actividad_aprendizaje_id);


-- migrate:down

ALTER TABLE seccion_actividad     DROP CONSTRAINT IF EXISTS seccion_actividad_nombre_aa_unique;
ALTER TABLE actividad_aprendizaje DROP CONSTRAINT IF EXISTS actividad_aprendizaje_nombre_ap_unique;
ALTER TABLE actividad_proyecto     DROP CONSTRAINT IF EXISTS actividad_proyecto_nombre_fase_unique;
