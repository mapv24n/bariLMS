CREATE TABLE usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            correo TEXT UNIQUE NOT NULL,
            contrasena_hash TEXT NOT NULL,
            rol TEXT NOT NULL,
            nombre TEXT NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1,
            creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE regional (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        );
CREATE TABLE centro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_regional INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_regional) REFERENCES regional(id) ON DELETE CASCADE
        );
CREATE TABLE coordinacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_centro INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_centro) REFERENCES centro(id) ON DELETE CASCADE
        );
CREATE TABLE sede (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_centro INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_centro) REFERENCES centro(id) ON DELETE CASCADE
        );
CREATE TABLE instructor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_coordinacion INTEGER NOT NULL,
            documento TEXT NOT NULL,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            correo TEXT,
            id_usuario INTEGER, id_area INTEGER, genero TEXT DEFAULT 'M',
            FOREIGN KEY (id_coordinacion) REFERENCES coordinacion(id) ON DELETE CASCADE
        );
CREATE TABLE aprendiz (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_coordinacion INTEGER NOT NULL,
            documento TEXT NOT NULL,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            ficha TEXT,
            FOREIGN KEY (id_coordinacion) REFERENCES coordinacion(id) ON DELETE CASCADE
        );
CREATE TABLE ambiente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_sede INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            capacidad INTEGER,
            FOREIGN KEY (id_sede) REFERENCES sede(id) ON DELETE CASCADE
        );
CREATE TABLE red_conocimiento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        );
CREATE TABLE area (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_red_conocimiento INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_red_conocimiento) REFERENCES red_conocimiento(id) ON DELETE CASCADE
        );
CREATE TABLE nivel_formacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        );
CREATE TABLE programa_formacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_area INTEGER NOT NULL,
            id_nivel_formacion INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_area) REFERENCES area(id) ON DELETE CASCADE,
            FOREIGN KEY (id_nivel_formacion) REFERENCES nivel_formacion(id) ON DELETE CASCADE
        );
CREATE TABLE ficha_formacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL UNIQUE,
            id_programa_formacion INTEGER NOT NULL,
            id_proyecto_formativo INTEGER,
            id_coordinacion INTEGER NOT NULL,
            id_instructor INTEGER,
            FOREIGN KEY (id_programa_formacion) REFERENCES programa_formacion(id) ON DELETE CASCADE,
            FOREIGN KEY (id_proyecto_formativo) REFERENCES proyecto_formativo(id) ON DELETE SET NULL,
            FOREIGN KEY (id_coordinacion) REFERENCES coordinacion(id) ON DELETE CASCADE,
            FOREIGN KEY (id_instructor) REFERENCES instructor(id) ON DELETE SET NULL
        );
CREATE TABLE proyecto_formativo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL
        );
CREATE TABLE fase_proyecto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_proyecto_formativo INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_proyecto_formativo) REFERENCES proyecto_formativo(id) ON DELETE CASCADE
        );
CREATE TABLE actividad_proyecto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_fase_proyecto INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_fase_proyecto) REFERENCES fase_proyecto(id) ON DELETE CASCADE
        );
CREATE TABLE actividad_aprendizaje (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_actividad_proyecto INTEGER NOT NULL,
            nombre TEXT NOT NULL, descripcion TEXT, fecha_inicio TEXT, fecha_fin TEXT, sub_seccion TEXT,
            FOREIGN KEY (id_actividad_proyecto) REFERENCES actividad_proyecto(id) ON DELETE CASCADE
        );
CREATE TABLE guia_aprendizaje (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_actividad_aprendizaje INTEGER NOT NULL UNIQUE,
            url TEXT NOT NULL,
            subido_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_actividad_aprendizaje) REFERENCES actividad_aprendizaje(id) ON DELETE CASCADE
        );
CREATE TABLE evidencia_aprendizaje (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_actividad_aprendizaje INTEGER NOT NULL,
            descripcion TEXT,
            creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_actividad_aprendizaje) REFERENCES actividad_aprendizaje(id) ON DELETE CASCADE
        );
CREATE TABLE entrega_evidencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_evidencia_aprendizaje INTEGER NOT NULL,
            id_usuario INTEGER NOT NULL,
            url TEXT NOT NULL,
            calificacion REAL,
            observaciones TEXT,
            entregado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_evidencia_aprendizaje) REFERENCES evidencia_aprendizaje(id) ON DELETE CASCADE,
            FOREIGN KEY (id_usuario) REFERENCES usuario(id) ON DELETE CASCADE
        );
CREATE TABLE ficha_instructor_competencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_ficha INTEGER NOT NULL,
            id_instructor INTEGER NOT NULL,
            UNIQUE(id_ficha, id_instructor),
            FOREIGN KEY (id_ficha) REFERENCES ficha_formacion(id) ON DELETE CASCADE,
            FOREIGN KEY (id_instructor) REFERENCES instructor(id) ON DELETE CASCADE
        );
CREATE TABLE seccion_actividad (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_actividad_aprendizaje INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            orden INTEGER DEFAULT 0,
            FOREIGN KEY (id_actividad_aprendizaje) REFERENCES actividad_aprendizaje(id) ON DELETE CASCADE
        );
CREATE TABLE sub_seccion_actividad (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_seccion INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            archivo_url TEXT,
            archivo_tipo TEXT,
            fecha_inicio TEXT,
            fecha_fin TEXT,
            orden INTEGER DEFAULT 0,
            FOREIGN KEY (id_seccion) REFERENCES seccion_actividad(id) ON DELETE CASCADE
        );
