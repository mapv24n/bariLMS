-- ============================================================
-- Script de setup para funcionalidades de la vista Aprendiz
-- Ejecutar en TablePlus sobre la BD senalearn
-- ============================================================

-- Fases del proceso formativo SENA
CREATE TABLE IF NOT EXISTS fases (
  id INT(11) NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(150) NOT NULL,
  orden TINYINT(3) NOT NULL DEFAULT 1,
  descripcion TEXT DEFAULT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Actividades de proyecto (agrupadas por fase)
CREATE TABLE IF NOT EXISTS actividades_proyecto (
  id INT(11) NOT NULL AUTO_INCREMENT,
  ficha_id INT(11) NOT NULL,
  fase_id INT(11) NOT NULL,
  nombre VARCHAR(200) NOT NULL,
  codigo VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY ficha_id (ficha_id),
  KEY fase_id (fase_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Actividades de aprendizaje (dentro de cada actividad de proyecto)
CREATE TABLE IF NOT EXISTS actividades_aprendizaje (
  id INT(11) NOT NULL AUTO_INCREMENT,
  actividad_proyecto_id INT(11) NOT NULL,
  nombre VARCHAR(200) NOT NULL,
  descripcion TEXT DEFAULT NULL,
  url_guia VARCHAR(500) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY actividad_proyecto_id (actividad_proyecto_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Entregas de evidencias y calificaciones
CREATE TABLE IF NOT EXISTS entrega_evidencia (
  id INT(11) NOT NULL AUTO_INCREMENT,
  aprendiz_id INT(11) NOT NULL,
  actividad_aprendizaje_id INT(11) NOT NULL,
  url_evidencia VARCHAR(1000) NOT NULL,
  fecha_entrega TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  calificacion TINYINT(3) UNSIGNED DEFAULT NULL,
  aprueba TINYINT(1) DEFAULT NULL,
  retroalimentacion TEXT DEFAULT NULL,
  calificado_en TIMESTAMP DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_aprendiz_actividad (aprendiz_id, actividad_aprendizaje_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Notificaciones para el aprendiz
CREATE TABLE IF NOT EXISTS notificaciones (
  id INT(11) NOT NULL AUTO_INCREMENT,
  usuario_id INT(11) NOT NULL,
  mensaje VARCHAR(500) NOT NULL,
  tipo ENUM('info','success','warning','danger') NOT NULL DEFAULT 'info',
  leida TINYINT(1) NOT NULL DEFAULT 0,
  url_destino VARCHAR(500) DEFAULT NULL,
  creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  PRIMARY KEY (id),
  KEY usuario_id (usuario_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Datos de prueba: 3 fases estándar SENA
INSERT IGNORE INTO fases (id, nombre, orden, descripcion) VALUES
(1, 'Análisis', 1, 'Identificación del proyecto formativo y reconocimiento del entorno productivo.'),
(2, 'Planeación', 2, 'Diseño y estructuración de las actividades del proyecto formativo.'),
(3, 'Ejecución', 3, 'Desarrollo de las actividades y entrega de evidencias de aprendizaje.');
