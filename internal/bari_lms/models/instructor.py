"""Modelo de Instructor – acceso a datos con PostgreSQL."""

from __future__ import annotations

from typing import Optional


class Instructor:
    """Encapsula las consultas relacionadas con la tabla `instructor`
    y sus tablas asociadas (fichas, fases, evidencias, entregas).

    Uso típico en una ruta Flask:
        db = get_db()
        instructor = Instructor.por_usuario(db, user["id"])
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(self, row):
        """Inicializa desde una fila de psycopg o dict."""
        self._id: int = row["id"]
        self._id_centro: int = row["id_centro"]
        self._documento: str = row["documento"]
        self._nombres: str = row["nombres"]
        self._apellidos: str = row["apellidos"]
        self._correo: Optional[str] = row["correo"]
        self._id_usuario: Optional[int] = row["id_usuario"]
        self._genero: str = row["genero"] or "M"

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------

    def get_id(self) -> int:
        return self._id

    def get_id_centro(self) -> int:
        return self._id_centro

    def get_documento(self) -> str:
        return self._documento

    def get_nombres(self) -> str:
        return self._nombres

    def get_apellidos(self) -> str:
        return self._apellidos

    def get_correo(self) -> Optional[str]:
        return self._correo

    def get_id_usuario(self) -> Optional[int]:
        return self._id_usuario

    def get_genero(self) -> str:
        return self._genero

    def get_nombre_completo(self) -> str:
        return f"{self._nombres} {self._apellidos}"

    def get_titulo(self) -> str:
        """Retorna 'Instructor' o 'Instructora' según el género."""
        return "Instructora" if self._genero == "F" else "Instructor"

    # ------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------

    def set_id_centro(self, valor: int) -> None:
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("id_centro debe ser un entero positivo.")
        self._id_centro = valor

    def set_documento(self, valor: str) -> None:
        valor = valor.strip()
        if not valor:
            raise ValueError("El documento no puede estar vacío.")
        self._documento = valor

    def set_nombres(self, valor: str) -> None:
        valor = valor.strip()
        if not valor:
            raise ValueError("El campo nombres no puede estar vacío.")
        self._nombres = valor

    def set_apellidos(self, valor: str) -> None:
        valor = valor.strip()
        if not valor:
            raise ValueError("El campo apellidos no puede estar vacío.")
        self._apellidos = valor

    def set_correo(self, valor: Optional[str]) -> None:
        if valor is not None:
            valor = valor.strip()
            if valor and "@" not in valor:
                raise ValueError("El correo no tiene un formato válido.")
            self._correo = valor or None
        else:
            self._correo = None

    def set_id_usuario(self, valor: Optional[int]) -> None:
        if valor is not None and (not isinstance(valor, int) or valor <= 0):
            raise ValueError("id_usuario debe ser un entero positivo o None.")
        self._id_usuario = valor

    def set_genero(self, valor: str) -> None:
        valor = valor.upper().strip()
        if valor not in ("M", "F"):
            raise ValueError("El género debe ser 'M' o 'F'.")
        self._genero = valor

    # ------------------------------------------------------------------
    # Consultas de búsqueda
    # ------------------------------------------------------------------

    @classmethod
    def por_usuario(cls, db, id_usuario: int) -> Optional["Instructor"]:
        """Retorna el Instructor vinculado a un usuario, o None."""
        row = db.execute(
            "SELECT * FROM instructor WHERE id_usuario = ?", (id_usuario,)
        ).fetchone()
        return cls(row) if row else None

    @classmethod
    def por_id(cls, db, id_instructor: int) -> Optional["Instructor"]:
        """Retorna el Instructor por su PK, o None."""
        row = db.execute(
            "SELECT * FROM instructor WHERE id = ?", (id_instructor,)
        ).fetchone()
        return cls(row) if row else None

    @classmethod
    def todos(cls, db) -> list["Instructor"]:
        """Retorna todos los instructores."""
        rows = db.execute(
            "SELECT * FROM instructor ORDER BY apellidos, nombres"
        ).fetchall()
        return [cls(r) for r in rows]

    # ------------------------------------------------------------------
    # Fichas
    # ------------------------------------------------------------------

    def fichas(self, db) -> list:
        """Retorna las fichas donde este instructor es líder (id_instructor)."""
        return db.execute(
            """
            SELECT f.id, f.numero,
                   p.nombre  AS programa_nombre,
                   pf.nombre AS proyecto_nombre,
                   pf.codigo AS proyecto_codigo,
                   n.nombre  AS nivel_nombre
            FROM ficha_formacion f
            JOIN programa_formacion   p  ON p.id  = f.id_programa_formacion
            LEFT JOIN proyecto_formativo pf ON pf.id = f.id_proyecto_formativo
            LEFT JOIN nivel_formacion    n  ON n.id  = p.id_nivel_formacion
            WHERE f.id_instructor = ?
            ORDER BY f.numero ASC
            """,
            (self._id,),
        ).fetchall()

    def fichas_por_competencia(self, db) -> list:
        """Retorna las fichas asignadas vía ficha_instructor_competencia."""
        return db.execute(
            """
            SELECT f.id, f.numero,
                   p.nombre  AS programa_nombre,
                   pf.nombre AS proyecto_nombre,
                   pf.codigo AS proyecto_codigo,
                   n.nombre  AS nivel_nombre
            FROM ficha_instructor_competencia fic
            JOIN ficha_formacion      f  ON f.id  = fic.id_ficha
            JOIN programa_formacion   p  ON p.id  = f.id_programa_formacion
            LEFT JOIN proyecto_formativo pf ON pf.id = f.id_proyecto_formativo
            LEFT JOIN nivel_formacion    n  ON n.id  = p.id_nivel_formacion
            WHERE fic.id_instructor = ?
            ORDER BY f.numero ASC
            """,
            (self._id,),
        ).fetchall()

    def tiene_acceso_ficha(self, db, id_ficha: int) -> bool:
        """Verifica si el instructor es líder de la ficha."""
        row = db.execute(
            "SELECT id FROM ficha_formacion WHERE id = ? AND id_instructor = ?",
            (id_ficha, self._id),
        ).fetchone()
        return row is not None

    # ------------------------------------------------------------------
    # Guías de aprendizaje
    # ------------------------------------------------------------------

    @staticmethod
    def guardar_guia(db, id_actividad_aprendizaje: int, url: str) -> None:
        """Crea o actualiza la guía de aprendizaje de una actividad."""
        existe = db.execute(
            "SELECT id FROM guia_aprendizaje WHERE id_actividad_aprendizaje = ?",
            (id_actividad_aprendizaje,),
        ).fetchone()
        if existe:
            db.execute(
                "UPDATE guia_aprendizaje SET url = ?, subido_en = CURRENT_TIMESTAMP "
                "WHERE id_actividad_aprendizaje = ?",
                (url, id_actividad_aprendizaje),
            )
        else:
            db.execute(
                "INSERT INTO guia_aprendizaje (id_actividad_aprendizaje, url) VALUES (?, ?)",
                (id_actividad_aprendizaje, url),
            )
        db.commit()

    # ------------------------------------------------------------------
    # Evidencias de aprendizaje
    # ------------------------------------------------------------------

    @staticmethod
    def crear_evidencia(db, id_actividad_aprendizaje: int, descripcion: str) -> int:
        """Inserta una evidencia de aprendizaje y retorna su id."""
        row = db.execute(
            "INSERT INTO evidencia_aprendizaje (id_actividad_aprendizaje, descripcion) VALUES (?, ?) RETURNING id",
            (id_actividad_aprendizaje, descripcion),
        ).fetchone()
        db.commit()
        return row["id"]

    @staticmethod
    def calificar_entrega(
        db, id_entrega: int, calificacion: float, observaciones: str
    ) -> bool:
        """Registra calificación en entrega_evidencia. Retorna True si encontró la fila."""
        row = db.execute(
            "SELECT id FROM entrega_evidencia WHERE id = ?", (id_entrega,)
        ).fetchone()
        if row is None:
            return False
        db.execute(
            "UPDATE entrega_evidencia SET calificacion = ?, observaciones = ? WHERE id = ?",
            (calificacion, observaciones, id_entrega),
        )
        db.commit()
        return True

    # ------------------------------------------------------------------
    # Árbol del proyecto formativo
    # ------------------------------------------------------------------

    @staticmethod
    def arbol_fases(db, id_ficha: int) -> list[dict]:
        """Retorna el árbol Fase > ActProyecto > ActAprendizaje de una ficha."""
        ficha = db.execute(
            "SELECT id_proyecto_formativo FROM ficha_formacion WHERE id = ?", (id_ficha,)
        ).fetchone()
        if ficha is None or ficha["id_proyecto_formativo"] is None:
            return []

        proyecto_id = ficha["id_proyecto_formativo"]
        rows = db.execute(
            """
            SELECT fp.id  AS fase_id,    fp.nombre  AS fase_nombre,
                   ap.id  AS act_proy_id, ap.nombre AS act_proy_nombre,
                   aa.id  AS act_apr_id,  aa.nombre AS act_apr_nombre,
                   ga.url AS guia_url,
                   ea.id  AS evidencia_id
            FROM fase_proyecto fp
            LEFT JOIN actividad_proyecto    ap ON ap.id_fase_proyecto         = fp.id
            LEFT JOIN actividad_aprendizaje aa ON aa.id_actividad_proyecto    = ap.id
            LEFT JOIN guia_aprendizaje      ga ON ga.id_actividad_aprendizaje = aa.id
            LEFT JOIN evidencia_aprendizaje ea ON ea.id_actividad_aprendizaje = aa.id
            WHERE fp.id_proyecto_formativo = ?
            ORDER BY fp.id, ap.id, aa.id
            """,
            (proyecto_id,),
        ).fetchall()

        fases: dict[int, dict] = {}
        for row in rows:
            fid = row["fase_id"]
            if fid not in fases:
                fases[fid] = {"id": fid, "nombre": row["fase_nombre"], "actividades_proyecto": {}}

            apid = row["act_proy_id"]
            if apid and apid not in fases[fid]["actividades_proyecto"]:
                fases[fid]["actividades_proyecto"][apid] = {
                    "id": apid,
                    "nombre": row["act_proy_nombre"],
                    "actividades_aprendizaje": [],
                }

            if apid and row["act_apr_id"]:
                fases[fid]["actividades_proyecto"][apid]["actividades_aprendizaje"].append(
                    {
                        "id": row["act_apr_id"],
                        "nombre": row["act_apr_nombre"],
                        "guia_url": row["guia_url"],
                        "evidencia_id": row["evidencia_id"],
                    }
                )

        result = []
        for fase in fases.values():
            fase["actividades_proyecto"] = list(fase["actividades_proyecto"].values())
            result.append(fase)
        return result
