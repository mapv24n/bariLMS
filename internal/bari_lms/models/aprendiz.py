"""Modelo Aprendiz — representa un aprendiz en Etapa Productiva.

Construido desde la fila devuelta por
InstructorEtapaProductivaService.get_aprendiz_completo().
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class Aprendiz:
    # Identidad
    aprendiz_id: str
    nombres: str
    apellidos: str
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    correo_personal: Optional[str] = None
    regional: Optional[str] = None

    # Contrato activo (None si no tiene proceso iniciado)
    contrato_id: Optional[str] = None
    contrato_estado: Optional[str] = None
    fecha_inicio: Optional[datetime.date] = None
    fecha_fin: Optional[datetime.date] = None

    # Empresa del contrato activo
    empresa_nombre: Optional[str] = None
    empresa_nit: Optional[str] = None
    empresa_correo: Optional[str] = None
    empresa_telefono: Optional[str] = None
    empresa_direccion: Optional[str] = None

    # ------------------------------------------------------------------ #
    # Propiedades de conveniencia
    # ------------------------------------------------------------------ #

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}"

    def fecha_inicio_str(self, fmt: str = "%d/%m/%Y") -> str:
        return self.fecha_inicio.strftime(fmt) if self.fecha_inicio else ""

    def fecha_fin_str(self, fmt: str = "%d/%m/%Y") -> str:
        return self.fecha_fin.strftime(fmt) if self.fecha_fin else ""

    # ------------------------------------------------------------------ #
    # Constructor desde fila psycopg
    # ------------------------------------------------------------------ #

    @classmethod
    def desde_fila(cls, row) -> "Aprendiz":
        """Construye un Aprendiz desde una fila de psycopg (dict_row)."""
        return cls(
            aprendiz_id=str(row["aprendiz_id"]),
            nombres=row["nombres"],
            apellidos=row["apellidos"],
            tipo_documento=row.get("tipo_documento"),
            numero_documento=row.get("numero_documento"),
            correo_personal=row.get("correo_personal"),
            regional=row.get("regional"),
            contrato_id=str(row["contrato_id"]) if row.get("contrato_id") else None,
            contrato_estado=row.get("contrato_estado"),
            fecha_inicio=row.get("fecha_inicio"),
            fecha_fin=row.get("fecha_fin"),
            empresa_nombre=row.get("empresa_nombre"),
            empresa_nit=row.get("empresa_nit"),
            empresa_correo=row.get("empresa_correo"),
            empresa_telefono=row.get("empresa_telefono"),
            empresa_direccion=row.get("empresa_direccion"),
        )
