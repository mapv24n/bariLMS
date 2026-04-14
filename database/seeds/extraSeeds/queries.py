from enum import Enum

class SeedQueries(Enum):
    # --- Catalogs ---
    INSERT_TIPO_DOC = """
        INSERT INTO tipo_documento (id, codigo, nombre)
        VALUES (%s, %s, %s) ON CONFLICT (codigo) DO NOTHING
    """
    
    INSERT_SEXO = """
        INSERT INTO sexo (id, codigo, nombre)
        VALUES (%s, %s, %s) ON CONFLICT (codigo) DO NOTHING
    """

    INSERT_NIVEL_FORMACION = """
        INSERT INTO nivel_formacion (id, nombre)
        VALUES (%s, %s) ON CONFLICT (nombre) DO NOTHING
    """

    # --- Institutional Structure ---
    INSERT_REGIONAL = """
        INSERT INTO regional (id, nombre)
        VALUES (%s, %s) ON CONFLICT (nombre) DO NOTHING
    """

    INSERT_CENTRO = """
        INSERT INTO centro (id, regional_id, nombre)
        VALUES (%s, %s, %s) ON CONFLICT (nombre) DO NOTHING
    """

    INSERT_COORDINACION = """
        INSERT INTO coordinacion (id, centro_id, nombre)
        VALUES (%s, %s, %s) ON CONFLICT (nombre) DO NOTHING
    """

    # --- Knowledge Area & Programs ---
    INSERT_RED = """
        INSERT INTO red_conocimiento (id, nombre)
        VALUES (%s, %s) ON CONFLICT (nombre) DO NOTHING
    """

    INSERT_AREA = """
        INSERT INTO area (id, red_conocimiento_id, nombre)
        VALUES (%s, %s, %s) ON CONFLICT (nombre) DO NOTHING
    """

    INSERT_PROGRAMA = """
        INSERT INTO programa_formacion (id, area_id, nivel_formacion_id, nombre)
        VALUES (%s, %s, %s, %s) ON CONFLICT (nombre) DO NOTHING
    """

    # --- Projects & Phases ---
    INSERT_PROYECTO = """
        INSERT INTO proyecto_formativo (id, codigo, nombre)
        VALUES (%s, %s, %s) ON CONFLICT (codigo) DO NOTHING
    """

    INSERT_FASE = """
        INSERT INTO fase_proyecto (id, proyecto_formativo_id, nombre)
        VALUES (%s, %s, %s) ON CONFLICT (nombre, proyecto_formativo_id) DO NOTHING
    """

    # --- Users & Instructors ---
    INSERT_USUARIO = """
        INSERT INTO usuario (id, correo, contrasena_hash, nombre, activo)
        VALUES (%s, %s, %s, %s, TRUE) ON CONFLICT (correo) DO NOTHING
    """

    INSERT_PERSONA = """
        INSERT INTO persona (id, tipo_documento_id, numero_documento, nombres, apellidos, sexo_id)
        VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
    """

    INSERT_INSTRUCTOR = """
        INSERT INTO instructor (id, persona_id, centro_id, area_id)
        VALUES (%s, %s, %s, %s) ON CONFLICT (persona_id) DO NOTHING
    """

    INSERT_PERFIL_LINK = """
        INSERT INTO usuario_perfil (id, usuario_id, perfil_id)
        VALUES (%s, %s, %s) ON CONFLICT (usuario_id, perfil_id) DO NOTHING
    """

    INSERT_FICHA = """
        INSERT INTO ficha_formacion 
        (id, numero, programa_formacion_id, coordinacion_id, proyecto_formativo_id, instructor_id)
        VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (numero) DO NOTHING
    """
    INSERT_EMPRESA = """
        INSERT INTO empresa (id, razon_social, nit, sector, correo, telefono)
        VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (nit) DO NOTHING
    """


    # --- Apprentice Specific ---

    INSERT_APRENDIZ = """
        INSERT INTO aprendiz (id, persona_id, regional_id)
        VALUES (%s, %s, %s) ON CONFLICT (persona_id) DO NOTHING
    """


    # --- Enrollment (Ficha-Aprendiz) ---

    INSERT_FICHA_APRENDIZ = """
        INSERT INTO ficha_aprendiz (id, ficha_id, aprendiz_id, estado)
        VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING
    """
    
    

    # ── Activity Content ───────────────────────────────────────────────────────
    INSERT_ACTIVIDAD_PROYECTO = """
        INSERT INTO actividad_proyecto (id, fase_proyecto_id, nombre, creado_por)
        VALUES (%s, %s, %s, %s) ON CONFLICT (nombre, fase_proyecto_id) DO NOTHING
    """

    INSERT_ACTIVIDAD_APRENDIZAJE = """
        INSERT INTO actividad_aprendizaje
            (id, actividad_proyecto_id, nombre, descripcion, fecha_inicio, fecha_fin, orden, creado_por)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (nombre, actividad_proyecto_id) DO NOTHING
    """

    INSERT_GUIA_APRENDIZAJE = """
        INSERT INTO guia_aprendizaje (id, actividad_aprendizaje_id, url, creado_por)
        VALUES (%s, %s, %s, %s) ON CONFLICT (actividad_aprendizaje_id) DO NOTHING
    """

    INSERT_SECCION_ACTIVIDAD = """
        INSERT INTO seccion_actividad
            (id, actividad_aprendizaje_id, nombre, descripcion, orden, creado_por)
        VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (nombre, actividad_aprendizaje_id) DO NOTHING
    """

    INSERT_SUB_SECCION_ACTIVIDAD = """
        INSERT INTO sub_seccion_actividad
            (id, seccion_id, nombre, descripcion, orden, creado_por)
        VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
    """

    def execute(self, cur, params):
        """
        Executes the query associated with the enum member.
        Returns True if a row was actually inserted.
        """
        cur.execute(self.value, params)
        return cur.rowcount > 0