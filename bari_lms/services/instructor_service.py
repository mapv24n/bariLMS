"""Capa de servicio para el Instructor.

Coordina la lógica de negocio entre las rutas Flask y el modelo Instructor.
Las rutas solo llaman a InstructorService; el modelo solo accede a la BD.
"""

from __future__ import annotations

from typing import Optional

from bari_lms.models.instructor import Instructor


class InstructorService:
    """Servicios de negocio relacionados con el Instructor."""

    # ------------------------------------------------------------------
    # Consultas de perfil
    # ------------------------------------------------------------------

    @staticmethod
    def obtener_por_usuario(db, id_usuario: int) -> Optional[Instructor]:
        """Retorna el Instructor asociado al usuario de sesión, o None."""
        return Instructor.por_usuario(db, id_usuario)

    @staticmethod
    def obtener_por_id(db, id_instructor: int) -> Optional[Instructor]:
        """Retorna un Instructor por su PK, o None si no existe."""
        return Instructor.por_id(db, id_instructor)

    @staticmethod
    def listar_todos(db) -> list[Instructor]:
        """Retorna todos los instructores ordenados por apellido."""
        return Instructor.todos(db)

    # ------------------------------------------------------------------
    # Fichas
    # ------------------------------------------------------------------

    @staticmethod
    def obtener_fichas(db, id_usuario: int) -> dict:
        """Retorna las fichas del instructor autenticado.

        Returns:
            {"ok": True,  "fichas": [...], "instructor": Instructor}
            {"ok": False, "error": str}
        """
        instructor = Instructor.por_usuario(db, id_usuario)
        if instructor is None:
            return {"ok": False, "error": "No se encontró el perfil de instructor."}

        fichas = instructor.fichas(db)
        return {"ok": True, "fichas": fichas, "instructor": instructor}

    @staticmethod
    def verificar_acceso_ficha(db, id_usuario: int, id_ficha: int) -> dict:
        """Verifica que el instructor tenga acceso a una ficha concreta.

        Returns:
            {"ok": True,  "instructor": Instructor, "ficha": row}
            {"ok": False, "error": str}
        """
        instructor = Instructor.por_usuario(db, id_usuario)
        if instructor is None:
            return {"ok": False, "error": "No se encontró el perfil de instructor."}

        ficha = db.execute(
            """
            SELECT f.id, f.numero,
                   p.nombre  AS programa_nombre,
                   pf.nombre AS proyecto_nombre,
                   pf.codigo AS proyecto_codigo,
                   pf.id     AS proyecto_id,
                   n.nombre  AS nivel_nombre
            FROM ficha_formacion f
            JOIN programa_formacion      p  ON p.id  = f.id_programa_formacion
            LEFT JOIN proyecto_formativo pf ON pf.id = f.id_proyecto_formativo
            LEFT JOIN nivel_formacion    n  ON n.id  = p.id_nivel_formacion
            WHERE f.id = ?
            """,
            (id_ficha,),
        ).fetchone()

        if ficha is None:
            return {"ok": False, "error": "La ficha solicitada no existe."}

        if not instructor.tiene_acceso_ficha(db, id_ficha):
            return {"ok": False, "error": "No tienes acceso a esta ficha."}

        return {"ok": True, "instructor": instructor, "ficha": ficha}

    # ------------------------------------------------------------------
    # Árbol del proyecto formativo
    # ------------------------------------------------------------------

    @staticmethod
    def obtener_arbol_fases(db, id_ficha: int) -> dict:
        """Retorna el árbol Fase > ActProyecto > ActAprendizaje de una ficha.

        Returns:
            {"ok": True,  "fases": [...]}
            {"ok": False, "error": str}
        """
        fases = Instructor.arbol_fases(db, id_ficha)
        if fases is None:
            return {"ok": False, "error": "La ficha no tiene proyecto formativo asignado."}
        return {"ok": True, "fases": fases}

    # ------------------------------------------------------------------
    # Guías de aprendizaje
    # ------------------------------------------------------------------

    @staticmethod
    def guardar_guia(db, id_actividad: int, url: str) -> dict:
        """Crea o actualiza la guía de aprendizaje de una actividad.

        Returns:
            {"ok": True}
            {"ok": False, "error": str}
        """
        url = url.strip() if url else ""
        if not url:
            return {"ok": False, "error": "La URL de la guía no puede estar vacía."}

        Instructor.guardar_guia(db, id_actividad, url)
        return {"ok": True}

    # ------------------------------------------------------------------
    # Evidencias de aprendizaje
    # ------------------------------------------------------------------

    @staticmethod
    def crear_evidencia(db, id_actividad: int, descripcion: str) -> dict:
        """Registra una nueva evidencia de aprendizaje.

        Returns:
            {"ok": True,  "id": int}
            {"ok": False, "error": str}
        """
        descripcion = descripcion.strip() if descripcion else ""
        if not descripcion:
            return {"ok": False, "error": "La descripción de la evidencia no puede estar vacía."}

        actividad = db.execute(
            "SELECT id FROM actividad_aprendizaje WHERE id = ?", (id_actividad,)
        ).fetchone()
        if actividad is None:
            return {"ok": False, "error": "La actividad de aprendizaje no existe."}

        nuevo_id = Instructor.crear_evidencia(db, id_actividad, descripcion)
        return {"ok": True, "id": nuevo_id}

    # ------------------------------------------------------------------
    # Calificación de entregas
    # ------------------------------------------------------------------

    @staticmethod
    def calificar_entrega(
        db, id_entrega: int, calificacion: float, observaciones: str
    ) -> dict:
        """Registra la calificación de una entrega de evidencia.

        Regla de negocio: aprueba con 75 o más, sobre 100.

        Returns:
            {"ok": True,  "aprueba": bool}
            {"ok": False, "error": str}
        """
        if not (0 <= calificacion <= 100):
            return {"ok": False, "error": "La calificación debe estar entre 0 y 100."}

        exito = Instructor.calificar_entrega(db, id_entrega, calificacion, observaciones)
        if not exito:
            return {"ok": False, "error": "La entrega no existe."}

        return {"ok": True, "aprueba": calificacion >= 75}

    # ------------------------------------------------------------------
    # Actualizar perfil del instructor
    # ------------------------------------------------------------------

    @staticmethod
    def actualizar_perfil(
        db,
        id_instructor: int,
        nombres: str,
        apellidos: str,
        correo: Optional[str],
        genero: str,
    ) -> dict:
        """Actualiza los datos personales del instructor en la BD.

        Returns:
            {"ok": True,  "instructor": Instructor}
            {"ok": False, "error": str}
        """
        instructor = Instructor.por_id(db, id_instructor)
        if instructor is None:
            return {"ok": False, "error": "Instructor no encontrado."}

        try:
            instructor.set_nombres(nombres)
            instructor.set_apellidos(apellidos)
            instructor.set_correo(correo)
            instructor.set_genero(genero)
        except ValueError as e:
            return {"ok": False, "error": str(e)}

        db.execute(
            """
            UPDATE instructor
               SET nombres = ?, apellidos = ?, correo = ?, genero = ?
             WHERE id = ?
            """,
            (
                instructor.get_nombres(),
                instructor.get_apellidos(),
                instructor.get_correo(),
                instructor.get_genero(),
                instructor.get_id(),
            ),
        )
        db.commit()
        return {"ok": True, "instructor": instructor}
