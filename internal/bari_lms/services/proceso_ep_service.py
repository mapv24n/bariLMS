"""Servicio para el Proceso de Etapa Productiva.

Maneja CRUD de proceso_ep, ep_momento_1/2/3 y sus evaluaciones.
Los factores de evaluación se almacenan en ep_momento_2_evaluacion y
ep_momento_3_evaluacion, vinculados al catálogo ep_factor — sin JSON.
"""

from __future__ import annotations


class ProcesoEPService:

    # ------------------------------------------------------------------
    # Contrato y proceso
    # ------------------------------------------------------------------

    @staticmethod
    def get_contrato(db, ficha_id: str, aprendiz_id: str):
        """Contrato activo que vincula al aprendiz con la ficha."""
        return db.execute(
            """
            SELECT ca.id, ca.empresa_id, ca.fecha_inicio, ca.fecha_fin,
                   e.razon_social AS empresa_nombre, e.nit AS empresa_nit
            FROM   ficha_aprendiz fa
            JOIN   contrato_aprendizaje ca ON ca.ficha_aprendiz_id = fa.id
                                          AND ca.estado = 'activo'
            LEFT JOIN empresa e ON e.id = ca.empresa_id
            WHERE  fa.ficha_id   = ?
              AND  fa.aprendiz_id = ?
            """,
            (ficha_id, aprendiz_id),
        ).fetchone()

    @staticmethod
    def get_proceso(db, contrato_id: str):
        """Proceso EP asociado al contrato, o None."""
        return db.execute(
            "SELECT * FROM proceso_ep WHERE contrato_id = ?", (contrato_id,)
        ).fetchone()

    @staticmethod
    def crear_proceso(db, contrato_id: str, instructor_id: str) -> str:
        """Crea el proceso EP o devuelve el existente. Retorna el id."""
        row = db.execute(
            """
            INSERT INTO proceso_ep (contrato_id, instructor_id)
            VALUES (?, ?)
            ON CONFLICT (contrato_id) DO UPDATE
                SET instructor_id  = EXCLUDED.instructor_id,
                    actualizado_en = NOW()
            RETURNING id
            """,
            (contrato_id, instructor_id),
        ).fetchone()
        db.commit()
        return row["id"]

    # ------------------------------------------------------------------
    # Factores
    # ------------------------------------------------------------------

    @staticmethod
    def get_factores(db, proyecto_formativo_id: str | None) -> list:
        """Devuelve los factores aplicables al proyecto.

        Si el proyecto tiene entradas en ep_factor_proyecto se usan esas.
        En caso contrario se devuelven todos los factores del catálogo.
        """
        if proyecto_formativo_id:
            custom = db.execute(
                """
                SELECT ef.id, ef.codigo, ef.nombre, ef.tipo, ef.orden
                FROM   ep_factor ef
                JOIN   ep_factor_proyecto efp ON efp.factor_id = ef.id
                WHERE  efp.proyecto_formativo_id = ?
                ORDER  BY ef.tipo, ef.orden
                """,
                (proyecto_formativo_id,),
            ).fetchall()
            if custom:
                return custom

        return db.execute(
            "SELECT id, codigo, nombre, tipo, orden FROM ep_factor ORDER BY tipo, orden"
        ).fetchall()

    # ------------------------------------------------------------------
    # Lectura de momentos
    # ------------------------------------------------------------------

    @staticmethod
    def get_momento_1(db, proceso_id: str):
        return db.execute(
            "SELECT * FROM ep_momento_1 WHERE proceso_id = ?", (proceso_id,)
        ).fetchone()

    @staticmethod
    def get_momento_2(db, proceso_id: str):
        return db.execute(
            "SELECT * FROM ep_momento_2 WHERE proceso_id = ?", (proceso_id,)
        ).fetchone()

    @staticmethod
    def get_momento_3(db, proceso_id: str):
        return db.execute(
            "SELECT * FROM ep_momento_3 WHERE proceso_id = ?", (proceso_id,)
        ).fetchone()

    @staticmethod
    def get_evaluaciones_m2(db, momento_id: str) -> dict:
        """Retorna {factor_id: {valoracion, observaciones}} para momento 2."""
        rows = db.execute(
            "SELECT factor_id, valoracion, observaciones FROM ep_momento_2_evaluacion WHERE momento_id = ?",
            (momento_id,),
        ).fetchall()
        return {
            r["factor_id"]: {"valoracion": r["valoracion"] or "", "observaciones": r["observaciones"] or ""}
            for r in rows
        }

    @staticmethod
    def get_evaluaciones_m3(db, momento_id: str) -> dict:
        """Retorna {factor_id: {valoracion, observaciones}} para momento 3."""
        rows = db.execute(
            "SELECT factor_id, valoracion, observaciones FROM ep_momento_3_evaluacion WHERE momento_id = ?",
            (momento_id,),
        ).fetchall()
        return {
            r["factor_id"]: {"valoracion": r["valoracion"] or "", "observaciones": r["observaciones"] or ""}
            for r in rows
        }

    # ------------------------------------------------------------------
    # Escritura de momentos
    # ------------------------------------------------------------------

    @staticmethod
    def guardar_momento_1(db, proceso_id: str, f: dict) -> None:
        """Inserta o actualiza ep_momento_1 para el proceso dado."""
        db.execute(
            """
            INSERT INTO ep_momento_1 (
                proceso_id,
                fecha_inicio_ep, fecha_fin_ep,
                arl_fecha_afiliacion, arl_poliza_numero,
                jornada, dias_semana, hora, url_grabacion,
                competencias, resultados_aprendizaje,
                actividades, evidencias, observaciones,
                firma_aprendiz, firma_instructor, firma_coformador,
                ciudad, fecha_firma, modalidad_firma
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (proceso_id) DO UPDATE SET
                fecha_inicio_ep        = EXCLUDED.fecha_inicio_ep,
                fecha_fin_ep           = EXCLUDED.fecha_fin_ep,
                arl_fecha_afiliacion   = EXCLUDED.arl_fecha_afiliacion,
                arl_poliza_numero      = EXCLUDED.arl_poliza_numero,
                jornada                = EXCLUDED.jornada,
                dias_semana            = EXCLUDED.dias_semana,
                hora                   = EXCLUDED.hora,
                url_grabacion          = EXCLUDED.url_grabacion,
                competencias           = EXCLUDED.competencias,
                resultados_aprendizaje = EXCLUDED.resultados_aprendizaje,
                actividades            = EXCLUDED.actividades,
                evidencias             = EXCLUDED.evidencias,
                observaciones          = EXCLUDED.observaciones,
                firma_aprendiz         = EXCLUDED.firma_aprendiz,
                firma_instructor       = EXCLUDED.firma_instructor,
                firma_coformador       = EXCLUDED.firma_coformador,
                ciudad                 = EXCLUDED.ciudad,
                fecha_firma            = EXCLUDED.fecha_firma,
                modalidad_firma        = EXCLUDED.modalidad_firma,
                actualizado_en         = NOW()
            """,
            (
                proceso_id,
                f.get("fecha_inicio_ep") or None,
                f.get("fecha_fin_ep") or None,
                f.get("fecha_arl") or None,
                f.get("poliza_arl") or None,
                f.get("jornada") or None,
                f.get("dias_semana") or None,
                f.get("hora") or None,
                f.get("url_grabacion") or None,
                f.get("competencias") or None,
                f.get("resultados_aprendizaje") or None,
                f.get("actividades") or None,
                f.get("evidencias") or None,
                f.get("observaciones") or None,
                "firma_aprendiz"   in f,
                "firma_instructor" in f,
                "firma_coformador" in f,
                f.get("ciudad") or None,
                f.get("fecha_firma") or None,
                f.get("modalidad_firma") or None,
            ),
        )
        db.commit()

    @staticmethod
    def guardar_momento_2(db, proceso_id: str, f: dict, factor_ids: list[str]) -> None:
        """Inserta o actualiza ep_momento_2 y sus evaluaciones por factor."""
        row = db.execute(
            """
            INSERT INTO ep_momento_2 (
                proceso_id,
                fecha_inicio_ep, fecha_momento,
                modalidad_seguimiento, url_grabacion,
                obs_instructor, obs_aprendiz, obs_coformador,
                firma_aprendiz, firma_instructor, firma_coformador,
                ciudad, fecha_firma, modalidad_firma
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (proceso_id) DO UPDATE SET
                fecha_inicio_ep       = EXCLUDED.fecha_inicio_ep,
                fecha_momento         = EXCLUDED.fecha_momento,
                modalidad_seguimiento = EXCLUDED.modalidad_seguimiento,
                url_grabacion         = EXCLUDED.url_grabacion,
                obs_instructor        = EXCLUDED.obs_instructor,
                obs_aprendiz          = EXCLUDED.obs_aprendiz,
                obs_coformador        = EXCLUDED.obs_coformador,
                firma_aprendiz        = EXCLUDED.firma_aprendiz,
                firma_instructor      = EXCLUDED.firma_instructor,
                firma_coformador      = EXCLUDED.firma_coformador,
                ciudad                = EXCLUDED.ciudad,
                fecha_firma           = EXCLUDED.fecha_firma,
                modalidad_firma       = EXCLUDED.modalidad_firma,
                actualizado_en        = NOW()
            RETURNING id
            """,
            (
                proceso_id,
                f.get("fecha_inicio_ep") or None,
                f.get("fecha_momento") or None,
                f.get("modalidad_seguimiento") or None,
                f.get("url_grabacion") or None,
                f.get("obs_instructor") or None,
                f.get("obs_aprendiz") or None,
                f.get("obs_coformador") or None,
                "firma_aprendiz"   in f,
                "firma_instructor" in f,
                "firma_coformador" in f,
                f.get("ciudad") or None,
                f.get("fecha_firma") or None,
                f.get("modalidad_firma") or None,
            ),
        ).fetchone()

        momento_id = row["id"]

        for factor_id in factor_ids:
            db.execute(
                """
                INSERT INTO ep_momento_2_evaluacion (momento_id, factor_id, valoracion, observaciones)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (momento_id, factor_id) DO UPDATE SET
                    valoracion    = EXCLUDED.valoracion,
                    observaciones = EXCLUDED.observaciones
                """,
                (
                    momento_id,
                    factor_id,
                    f.get(f"factor_{factor_id}_val") or None,
                    f.get(f"factor_{factor_id}_obs") or None,
                ),
            )

        db.commit()

    @staticmethod
    def guardar_momento_3(db, proceso_id: str, f: dict, factor_ids: list[str]) -> None:
        """Inserta o actualiza ep_momento_3 y sus evaluaciones por factor."""
        num_visitas = f.get("num_visitas")
        num_visitas = int(num_visitas) if num_visitas else None

        row = db.execute(
            """
            INSERT INTO ep_momento_3 (
                proceso_id,
                fecha_inicio_ep, fecha_fin_ep,
                num_visitas, modalidad_evaluacion, url_grabacion,
                retro_proceso_coformador, retro_desempeno_coformador,
                retro_proceso_instructor, retro_desempeno_instructor,
                retro_proceso_aprendiz,   retro_desempeno_aprendiz,
                juicio_resultado, juicio_observaciones,
                firma_aprendiz, firma_instructor, firma_coformador,
                ciudad, fecha_firma, modalidad_firma
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (proceso_id) DO UPDATE SET
                fecha_inicio_ep            = EXCLUDED.fecha_inicio_ep,
                fecha_fin_ep               = EXCLUDED.fecha_fin_ep,
                num_visitas                = EXCLUDED.num_visitas,
                modalidad_evaluacion       = EXCLUDED.modalidad_evaluacion,
                url_grabacion              = EXCLUDED.url_grabacion,
                retro_proceso_coformador   = EXCLUDED.retro_proceso_coformador,
                retro_desempeno_coformador = EXCLUDED.retro_desempeno_coformador,
                retro_proceso_instructor   = EXCLUDED.retro_proceso_instructor,
                retro_desempeno_instructor = EXCLUDED.retro_desempeno_instructor,
                retro_proceso_aprendiz     = EXCLUDED.retro_proceso_aprendiz,
                retro_desempeno_aprendiz   = EXCLUDED.retro_desempeno_aprendiz,
                juicio_resultado           = EXCLUDED.juicio_resultado,
                juicio_observaciones       = EXCLUDED.juicio_observaciones,
                firma_aprendiz             = EXCLUDED.firma_aprendiz,
                firma_instructor           = EXCLUDED.firma_instructor,
                firma_coformador           = EXCLUDED.firma_coformador,
                ciudad                     = EXCLUDED.ciudad,
                fecha_firma                = EXCLUDED.fecha_firma,
                modalidad_firma            = EXCLUDED.modalidad_firma,
                actualizado_en             = NOW()
            RETURNING id
            """,
            (
                proceso_id,
                f.get("fecha_inicio_ep") or None,
                f.get("fecha_fin_ep") or None,
                num_visitas,
                f.get("modalidad_evaluacion") or None,
                f.get("url_grabacion") or None,
                f.get("retro_proceso_coformador")    or None,
                f.get("retro_desempeno_coformador")  or None,
                f.get("retro_proceso_instructor")    or None,
                f.get("retro_desempeno_instructor")  or None,
                f.get("retro_proceso_aprendiz")      or None,
                f.get("retro_desempeno_aprendiz")    or None,
                f.get("juicio_resultado") or None,
                f.get("juicio_observaciones") or None,
                "firma_aprendiz"   in f,
                "firma_instructor" in f,
                "firma_coformador" in f,
                f.get("ciudad") or None,
                f.get("fecha_firma") or None,
                f.get("modalidad_firma") or None,
            ),
        ).fetchone()

        momento_id = row["id"]

        for factor_id in factor_ids:
            db.execute(
                """
                INSERT INTO ep_momento_3_evaluacion (momento_id, factor_id, valoracion, observaciones)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (momento_id, factor_id) DO UPDATE SET
                    valoracion    = EXCLUDED.valoracion,
                    observaciones = EXCLUDED.observaciones
                """,
                (
                    momento_id,
                    factor_id,
                    f.get(f"factor_{factor_id}_val") or None,
                    f.get(f"factor_{factor_id}_obs") or None,
                ),
            )

        db.commit()
