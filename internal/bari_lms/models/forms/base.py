"""Bloques de construcción para formularios EP.

Un formulario es una lista de FormSection.
Cada FormSection contiene una lista plana de FormField.
El tipo de cada campo es explícito — nunca se infiere.

Tipos de campo soportados:
    text          → <input type="text">
    date          → <input type="date">
    email         → <input type="email">
    tel           → <input type="tel">
    number        → <input type="number">
    textarea      → <textarea>
    checkbox      → <input type="checkbox">   (value: bool)
    checkbox-group→ varios checkboxes         (options: list[str], value: list[str])
    select        → <select>                  (options: list[str], value: str)
    eval-pair     → select valoración + textarea observaciones
                    (value: {"valoracion": "", "observaciones": ""})
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from typing import Any


@dataclass
class FormField:
    key: str                          # snake_case — usado en código y como name del input
    label: str                        # texto visible en el formulario
    type: str                         # uno de los tipos listados arriba
    value: Any = ""                   # valor pre-llenado (o vacío)
    options: list[str] = dc_field(default_factory=list)  # para select y checkbox-group

    def to_dict(self) -> dict:
        d = {
            "key":   self.key,
            "label": self.label,
            "type":  self.type,
            "value": self.value,
        }
        if self.options:
            d["options"] = self.options
        return d


@dataclass
class FormSection:
    id: str                           # snake_case — identifica la sección en el código
    label: str                        # encabezado visible
    fields: list[FormField] = dc_field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id":     self.id,
            "label":  self.label,
            "fields": [f.to_dict() for f in self.fields],
        }


def fill_section(sections: list[FormSection], section_id: str, key: str, value: Any) -> None:
    """Establece el valor de un campo en la sección indicada (muta la copia en lugar).

    Uso:
        sections = copy.deepcopy(INFORMACION_GENERAL)
        fill_section(sections, "datos_aprendiz", "nombre_completo", aprendiz.nombre_completo)
    """
    for section in sections:
        if section.id == section_id:
            for f in section.fields:
                if f.key == key:
                    f.value = value
                    return


def to_json_list(sections: list[FormSection]) -> list[dict]:
    """Convierte la lista de secciones a una lista de dicts lista para json.dumps()."""
    return [s.to_dict() for s in sections]
