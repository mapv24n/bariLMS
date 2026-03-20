-- ============================================================
-- Script de setup para funcionalidades de la vista Aprendiz
-- PostgreSQL syntax
-- ============================================================

-- Fases del proceso formativo SENA
CREATE TABLE IF NOT EXISTS fases (
  id      SERIAL NOT NULL,
  nombre  VARCHAR(150) NOT NULL,
  orden   SMALLINT NOT NULL DEFAULT 1,
  descripcion TEXT DEFAULT NULL,
  PRIMARY KEY (id)
);

-- Actividades de proyecto (agrupadas por fase)
CREATE TABLE IF NOT EXISTS actividades_proyecto (
  id        SERIAL NOT NULL,
  ficha_id  INTEGER NOT NULL,
  fase_id   INTEGER NOT NULL,
  nombre    VARCHAR(200) NOT NULL,
  codigo    VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS idx_actividades_proyecto_ficha_id ON actividades_proyecto (ficha_id);
CREATE INDEX IF NOT EXISTS idx_actividades_proyecto_fase_id  ON actividades_proyecto (fase_id);

-- Actividades de aprendizaje (dentro de cada actividad de proyecto)
CREATE TABLE IF NOT EXISTS actividades_aprendizaje (
  id                    SERIAL NOT NULL,
  actividad_proyecto_id INTEGER NOT NULL,
  nombre                VARCHAR(200) NOT NULL,
  descripcion           TEXT DEFAULT NULL,
  url_guia              VARCHAR(500) DEFAULT NULL,
  PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS idx_actividades_aprendizaje_ap_id ON actividades_aprendizaje (actividad_proyecto_id);

-- Entregas de evidencias y calificaciones
CREATE TABLE IF NOT EXISTS entrega_evidencia (
  id                        SERIAL NOT NULL,
  aprendiz_id               INTEGER NOT NULL,
  actividad_aprendizaje_id  INTEGER NOT NULL,
  url_evidencia             VARCHAR(1000) NOT NULL,
  fecha_entrega             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  calificacion              SMALLINT DEFAULT NULL,
  aprueba                   BOOLEAN DEFAULT NULL,
  retroalimentacion         TEXT DEFAULT NULL,
  calificado_en             TIMESTAMP DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE (aprendiz_id, actividad_aprendizaje_id)
);

-- Notificaciones para el aprendiz
CREATE TABLE IF NOT EXISTS notificaciones (
  id          SERIAL NOT NULL,
  usuario_id  INTEGER NOT NULL,
  mensaje     VARCHAR(500) NOT NULL,
  tipo        VARCHAR(10) NOT NULL DEFAULT 'info'
                CHECK (tipo IN ('info', 'success', 'warning', 'danger')),
  leida       BOOLEAN NOT NULL DEFAULT FALSE,
  url_destino VARCHAR(500) DEFAULT NULL,
  creado_en   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario_id ON notificaciones (usuario_id);

-- Datos de prueba: 3 fases estándar SENA
INSERT INTO fases (id, nombre, orden, descripcion) VALUES
(1, 'Análisis',   1, 'Identificación del proyecto formativo y reconocimiento del entorno productivo.'),
(2, 'Planeación', 2, 'Diseño y estructuración de las actividades del proyecto formativo.'),
(3, 'Ejecución',  3, 'Desarrollo de las actividades y entrega de evidencias de aprendizaje.')
ON CONFLICT DO NOTHING;
