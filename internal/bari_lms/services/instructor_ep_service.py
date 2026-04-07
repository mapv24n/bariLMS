"""Servicio de Etapa Productiva — logica de consultas para el instructor.

NOTE FOR AI ASSISTANTS (Claude and similar):
  - EP tables: empresa, ficha_aprendiz, contrato_aprendizaje.
  - ficha_aprendiz uses a single ENUM column `estado` (tipo estado_formacion_aprendiz).
    Values: lectiva_en_curso, lectiva_concluida, productiva_en_curso, productiva_concluida,
            trasladado, suspendido.
    The old boolean columns (en_etapa_lectiva, etapa_lectiva_concluida, en_etapa_productiva,
    etapa_productiva_concluida) were removed in migration 20260407000001.
  - "In productive stage" means: estado IN ('productiva_en_curso', 'productiva_concluida').
  - empresa_id, fecha_inicio_ep, fecha_fin_ep do not exist on ficha_aprendiz.
    Company assignment lives in contrato_aprendizaje (ficha_aprendiz_id + empresa_id).
  - Before editing queries here, verify the real schema with:
      python database/query.py "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'ficha_aprendiz' ORDER BY ordinal_position"
  - Validation: python database/query.py "SELECT estado, COUNT(*) FROM ficha_aprendiz GROUP BY estado ORDER BY estado"
  - Migration history: database/migrations/  (managed with Dbmate)
  - TOKEN WARNING: use database/query.py sparingly — pipe specific columns and LIMIT rows.
"""


class InstructorEtapaProductivaService:

    @staticmethod
    def get_instructor(db, usuario_id):
        """Obtiene el registro instructor cuyo persona_id coincide con usuario_id."""
        return db.execute(
            "SELECT id FROM instructor WHERE persona_id = ?", (usuario_id,)
        ).fetchone()

    @staticmethod
    def get_fichas_ep(db, instructor_id):
        """Fichas asignadas al instructor (CU003 — listado EP)."""
        return db.execute(
            """
            SELECT f.id, f.numero,
                   p.nombre  AS programa_nombre,
                   pf.nombre AS proyecto_nombre,
                   pf.codigo AS proyecto_codigo,
                   n.nombre  AS nivel_nombre
            FROM   ficha_formacion f
            JOIN   programa_formacion   p  ON p.id  = f.programa_formacion_id
            LEFT JOIN proyecto_formativo pf ON pf.id = f.proyecto_formativo_id
            LEFT JOIN nivel_formacion    n  ON n.id  = p.nivel_formacion_id
            WHERE  f.instructor_id = ?
            ORDER  BY f.numero ASC
            """,
            (instructor_id,),
        ).fetchall()

    @staticmethod
    def get_ficha(db, ficha_id):
        return db.execute(
            """
            SELECT f.id, f.numero,
                   p.nombre  AS programa_nombre,
                   pf.nombre AS proyecto_nombre,
                   pf.codigo AS proyecto_codigo,
                   n.nombre  AS nivel_nombre
            FROM   ficha_formacion f
            JOIN   programa_formacion   p  ON p.id  = f.programa_formacion_id
            LEFT JOIN proyecto_formativo pf ON pf.id = f.proyecto_formativo_id
            LEFT JOIN nivel_formacion    n  ON n.id  = p.nivel_formacion_id
            WHERE  f.id = ?
            """,
            (ficha_id,),
        ).fetchone()

    @staticmethod
    def ficha_pertenece_al_instructor(db, ficha_id, instructor_id):
        return db.execute(
            "SELECT id FROM ficha_formacion WHERE id = ? AND instructor_id = ?",
            (ficha_id, instructor_id),
        ).fetchone() is not None

    @staticmethod
    def get_aprendices_ep(db, ficha_id):
        """Aprendices en etapa productiva (en curso o concluida) para la ficha dada (CU004).

        La empresa y las fechas se obtienen del contrato activo en
        contrato_aprendizaje. Si el aprendiz aún no tiene contrato,
        empresa_nombre y empresa_nit serán NULL.
        """
        return db.execute(
            """
            SELECT
                fa.id                       AS inscripcion_id,
                fa.estado,
                ca.fecha_inicio             AS fecha_inicio_ep,
                ca.fecha_fin                AS fecha_fin_ep,
                a.id                        AS aprendiz_id,
                per.nombres,
                per.apellidos,
                per.numero_documento,
                td.nombre                   AS tipo_documento,
                e.razon_social              AS empresa_nombre,
                e.nit                       AS empresa_nit
            FROM   ficha_aprendiz fa
            JOIN   aprendiz  a   ON a.id   = fa.aprendiz_id
            JOIN   persona   per ON per.id = a.persona_id
            LEFT JOIN tipo_documento       td ON td.id = per.tipo_documento_id
            LEFT JOIN contrato_aprendizaje ca ON ca.ficha_aprendiz_id = fa.id
                                             AND ca.estado = 'activo'
            LEFT JOIN empresa              e  ON e.id  = ca.empresa_id
            WHERE  fa.ficha_id = ?
              AND  fa.estado IN ('productiva_en_curso', 'productiva_concluida')
            ORDER  BY per.apellidos, per.nombres
            """,
            (ficha_id,),
        ).fetchall()

    @staticmethod
    def get_aprendiz_proceso(db, ficha_id, aprendiz_id):
        """Datos del proceso EP de un aprendiz especifico (CU007).

        Retorna None si el aprendiz no pertenece a la ficha.
        contrato_id sera NULL si no tiene contrato activo (proceso no iniciado).
        """
        return db.execute(
            """
            SELECT
                fa.id                       AS inscripcion_id,
                fa.estado,
                a.id                        AS aprendiz_id,
                per.nombres,
                per.apellidos,
                per.numero_documento,
                td.nombre                   AS tipo_documento,
                ca.id                       AS contrato_id,
                ca.estado                   AS contrato_estado,
                ca.fecha_inicio,
                ca.fecha_fin,
                e.razon_social              AS empresa_nombre,
                e.nit                       AS empresa_nit
            FROM   ficha_aprendiz fa
            JOIN   aprendiz  a   ON a.id   = fa.aprendiz_id
            JOIN   persona   per ON per.id = a.persona_id
            LEFT JOIN tipo_documento       td ON td.id = per.tipo_documento_id
            LEFT JOIN contrato_aprendizaje ca ON ca.ficha_aprendiz_id = fa.id
                                             AND ca.estado = 'activo'
            LEFT JOIN empresa              e  ON e.id  = ca.empresa_id
            WHERE  fa.ficha_id   = ?
              AND  fa.aprendiz_id = ?
            """,
            (ficha_id, aprendiz_id),
        ).fetchone()

    @staticmethod
    def get_aprendiz_completo(db, ficha_id, aprendiz_id):
        """Datos completos del aprendiz para formularios EP (CU007+).

        Incluye correo_personal, regional y detalles de empresa del contrato activo.
        Retorna None si el aprendiz no pertenece a la ficha.
        """
        return db.execute(
            """
            SELECT
                fa.id                           AS inscripcion_id,
                fa.estado,
                a.id                            AS aprendiz_id,
                per.nombres,
                per.apellidos,
                per.numero_documento,
                per.correo_personal,
                td.nombre                       AS tipo_documento,
                r.nombre                        AS regional,
                ca.id                           AS contrato_id,
                ca.estado                       AS contrato_estado,
                ca.fecha_inicio,
                ca.fecha_fin,
                e.razon_social                  AS empresa_nombre,
                e.nit                           AS empresa_nit,
                e.correo                        AS empresa_correo,
                e.telefono                      AS empresa_telefono,
                e.direccion                     AS empresa_direccion
            FROM   ficha_aprendiz fa
            JOIN   aprendiz  a   ON a.id   = fa.aprendiz_id
            JOIN   persona   per ON per.id = a.persona_id
            LEFT JOIN tipo_documento       td ON td.id  = per.tipo_documento_id
            LEFT JOIN regional             r  ON r.id   = a.regional_id
            LEFT JOIN contrato_aprendizaje ca ON ca.ficha_aprendiz_id = fa.id
                                             AND ca.estado = 'activo'
            LEFT JOIN empresa              e  ON e.id   = ca.empresa_id
            WHERE  fa.ficha_id   = ?
              AND  fa.aprendiz_id = ?
            """,
            (ficha_id, aprendiz_id),
        ).fetchone()

    @staticmethod
    def get_instructor_info(db, instructor_id):
        """Nombre completo, centro y regional del instructor (para formularios EP)."""
        return db.execute(
            """
            SELECT
                per.nombres                     AS nombres,
                per.apellidos                   AS apellidos,
                c.nombre                        AS centro_nombre,
                r.nombre                        AS regional_nombre
            FROM   instructor  i
            JOIN   persona     per ON per.id = i.persona_id
            LEFT JOIN centro    c  ON c.id  = i.centro_id
            LEFT JOIN regional  r  ON r.id  = c.regional_id
            WHERE  i.id = ?
            """,
            (instructor_id,),
        ).fetchone()

    @staticmethod
    def get_empresas_ep(db, ficha_id):
        """Empresas con al menos un contrato activo en EP para la ficha dada (CU006).

        Solo devuelve empresas que tengan aprendices de esta ficha con un
        contrato_aprendizaje activo, garantizando que la empresa aparezca
        únicamente si la condición ficha ↔ aprendiz ↔ empresa se cumple.
        """
        return db.execute(
            """
            SELECT
                e.id            AS empresa_id,
                e.razon_social,
                e.nit,
                e.sector,
                e.correo,
                e.telefono,
                e.direccion,
                COUNT(ca.id)    AS total_aprendices
            FROM   ficha_aprendiz fa
            JOIN   contrato_aprendizaje ca ON ca.ficha_aprendiz_id = fa.id
                                           AND ca.estado = 'activo'
            JOIN   empresa e ON e.id = ca.empresa_id
            WHERE  fa.ficha_id = ?
              AND  fa.estado IN ('productiva_en_curso', 'productiva_concluida')
            GROUP BY e.id, e.razon_social, e.nit, e.sector, e.correo, e.telefono, e.direccion
            ORDER BY e.razon_social
            """,
            (ficha_id,),
        ).fetchall()
