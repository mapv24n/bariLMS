BEGIN;

CREATE TABLE IF NOT EXISTS usuario (
    id SERIAL PRIMARY KEY,
    correo TEXT UNIQUE NOT NULL,
    contrasena_hash TEXT NOT NULL,
    rol TEXT NOT NULL,
    nombre TEXT NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS regional (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS centro (
    id SERIAL PRIMARY KEY,
    id_regional INTEGER NOT NULL REFERENCES regional(id) ON DELETE CASCADE,
    nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS coordinacion (
    id SERIAL PRIMARY KEY,
    id_centro INTEGER NOT NULL REFERENCES centro(id) ON DELETE CASCADE,
    nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sede (
    id SERIAL PRIMARY KEY,
    id_centro INTEGER NOT NULL REFERENCES centro(id) ON DELETE CASCADE,
    nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS red_conocimiento (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS area (
    id SERIAL PRIMARY KEY,
    id_red_conocimiento INTEGER NOT NULL REFERENCES red_conocimiento(id) ON DELETE CASCADE,
    nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS nivel_formacion (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS proyecto_formativo (
    id SERIAL PRIMARY KEY,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fase_proyecto (
    id SERIAL PRIMARY KEY,
    id_proyecto_formativo INTEGER NOT NULL REFERENCES proyecto_formativo(id) ON DELETE CASCADE,
    nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS actividad_proyecto (
    id SERIAL PRIMARY KEY,
    id_fase_proyecto INTEGER NOT NULL REFERENCES fase_proyecto(id) ON DELETE CASCADE,
    nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS actividad_aprendizaje (
    id SERIAL PRIMARY KEY,
    id_actividad_proyecto INTEGER NOT NULL REFERENCES actividad_proyecto(id) ON DELETE CASCADE,
    nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS programa_formacion (
    id SERIAL PRIMARY KEY,
    id_area INTEGER NOT NULL REFERENCES area(id) ON DELETE CASCADE,
    id_nivel_formacion INTEGER NOT NULL REFERENCES nivel_formacion(id) ON DELETE CASCADE,
    nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS instructor (
    id SERIAL PRIMARY KEY,
    id_centro INTEGER NOT NULL REFERENCES centro(id) ON DELETE CASCADE,
    id_area INTEGER,
    documento TEXT NOT NULL,
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    correo TEXT,
    id_usuario INTEGER
);

CREATE TABLE IF NOT EXISTS aprendiz (
    id SERIAL PRIMARY KEY,
    id_regional INTEGER NOT NULL REFERENCES regional(id) ON DELETE CASCADE,
    documento TEXT NOT NULL,
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    correo TEXT,
    id_usuario INTEGER,
    ficha TEXT
);

CREATE TABLE IF NOT EXISTS personal_administrativo (
    id SERIAL PRIMARY KEY,
    id_centro INTEGER NOT NULL REFERENCES centro(id) ON DELETE CASCADE,
    documento TEXT NOT NULL,
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    correo TEXT,
    cargo TEXT NOT NULL,
    id_usuario INTEGER
);

CREATE TABLE IF NOT EXISTS ambiente (
    id SERIAL PRIMARY KEY,
    id_sede INTEGER NOT NULL REFERENCES sede(id) ON DELETE CASCADE,
    nombre TEXT NOT NULL,
    capacidad INTEGER
);

CREATE TABLE IF NOT EXISTS ficha_formacion (
    id SERIAL PRIMARY KEY,
    numero TEXT NOT NULL UNIQUE,
    id_programa_formacion INTEGER NOT NULL REFERENCES programa_formacion(id) ON DELETE CASCADE,
    id_proyecto_formativo INTEGER REFERENCES proyecto_formativo(id) ON DELETE SET NULL,
    id_coordinacion INTEGER NOT NULL REFERENCES coordinacion(id) ON DELETE CASCADE,
    id_instructor INTEGER REFERENCES instructor(id) ON DELETE SET NULL
);

INSERT INTO nivel_formacion (nombre) VALUES
    ('Técnico'),
    ('Tecnólogo'),
    ('Operario'),
    ('Auxiliar'),
    ('Curso')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO usuario (correo, contrasena_hash, rol, nombre, activo) VALUES
    ('admin@senalearn.edu.co', 'scrypt:32768:8:1$PawkpxdCWjHQajUa$1bdde7bd5b04f95622b19c721f72ae0ca6b4a7204e5580b9312a328628d2e67e8be87a697d47ed0a6e7d0f2e9bdee8ec41695c905ba6caa967fa1a22394c86d0', 'Administrador', 'Laura Moreno', TRUE),
    ('administrativo@senalearn.edu.co', 'scrypt:32768:8:1$krVtIj4OJzuKERQ1$4d2f97bbf5e307e37479ed9cef7b2538ec75a9e1466cbcf1a90eb2cb89facb9783b70b1f12fb053627cac8d906e7085aed3af853f65f25a085207aa369489d68', 'Administrativo', 'Carlos Ruiz', TRUE),
    ('instructor@senalearn.edu.co', 'scrypt:32768:8:1$E40zpf0IIu94bkMD$4c9051f6eb342131968701b79f4e35b4ebab4fe421700deab31e15134a52dff9fecd179a5d49b725e5e599526ed8815ca272917c2d7bdf3e70f45074974fdd6b', 'Instructor', 'Diana Beltrán', TRUE),
    ('aprendiz@senalearn.edu.co', 'scrypt:32768:8:1$hIo7knIThCQ6VGzO$a4e4292209ba0098141d6841934a76135bdb5e6bd2fd5028a7d7a2fbb06d1d546f0eb5d6b67f945de6f3429f279b48fdc8c73fa33d083f41bd2468ef59365ae9', 'Aprendiz', 'Miguel Torres', TRUE)
ON CONFLICT (correo) DO NOTHING;

COMMIT;
