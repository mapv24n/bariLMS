"""Servicio de formularios EP — llena los formularios con datos reales de BD.

Importa las definiciones de formulario desde models/forms/ y devuelve
copias profundas pre-llenadas, listas para json.dumps().

Uso en la ruta:
    from bari_lms.services.datos_seguimiento_ep import DatosSeguimientoEP
    import json

    form_ig = DatosSeguimientoEP.fill_informacion_general(
        aprendiz, instructor_nombre, instructor_correo,
        nivel=ficha["nivel_nombre"], programa=ficha["programa_nombre"],
        ficha_numero=ficha["numero"], centro=centro_nombre,
    )
    form_ig_json = json.dumps(form_ig, ensure_ascii=False)
"""

import copy

from bari_lms.models.aprendiz import Aprendiz
from bari_lms.models.forms.base import fill_section, to_json_list
from bari_lms.models.forms.informacion_general import INFORMACION_GENERAL
from bari_lms.models.forms.momento_1 import MOMENTO_1_PLANEACION
from bari_lms.models.forms.momento_2 import MOMENTO_2_SEGUIMIENTO
from bari_lms.models.forms.momento_3 import MOMENTO_3_EVALUACION


class DatosSeguimientoEP:

    @staticmethod
    def fill_informacion_general(
        aprendiz: Aprendiz,
        instructor_nombre: str,
        instructor_correo: str,
        nivel: str = "",
        programa: str = "",
        ficha_numero: str = "",
        centro: str = "",
        regional: str = "",
    ) -> list[dict]:
        """Devuelve INFORMACION_GENERAL pre-llenado, serializado como lista de dicts."""
        s = copy.deepcopy(INFORMACION_GENERAL)

        # ── Información general ───────────────────────────────────────────
        fill_section(s, "informacion_general", "regional",           regional or aprendiz.regional or "")
        fill_section(s, "informacion_general", "centro_formacion",   centro or "")
        fill_section(s, "informacion_general", "nivel_formativo",    nivel or "")
        fill_section(s, "informacion_general", "programa_formacion", programa or "")
        fill_section(s, "informacion_general", "no_grupo",           ficha_numero or "")

        # ── Datos del aprendiz ────────────────────────────────────────────
        fill_section(s, "datos_aprendiz", "nombre_completo",      aprendiz.nombre_completo)
        fill_section(s, "datos_aprendiz", "tipo_documento",       aprendiz.tipo_documento or "")
        fill_section(s, "datos_aprendiz", "numero_documento",     aprendiz.numero_documento or "")
        fill_section(s, "datos_aprendiz", "correo_personal",      aprendiz.correo_personal or "")

        # ── Instructor ────────────────────────────────────────────────────
        fill_section(s, "datos_instructor", "instructor_nombre",  instructor_nombre or "")
        fill_section(s, "datos_instructor", "instructor_correo",  instructor_correo or "")

        # ── Empresa / ente co-formador ────────────────────────────────────
        fill_section(s, "datos_empresa", "empresa_nombre",    aprendiz.empresa_nombre or "")
        fill_section(s, "datos_empresa", "empresa_nit",       aprendiz.empresa_nit or "")
        fill_section(s, "datos_empresa", "empresa_correo",    aprendiz.empresa_correo or "")
        fill_section(s, "datos_empresa", "empresa_telefono",  aprendiz.empresa_telefono or "")
        fill_section(s, "datos_empresa", "empresa_direccion", aprendiz.empresa_direccion or "")

        return to_json_list(s)

    @staticmethod
    def fill_momento_1(aprendiz: Aprendiz) -> list[dict]:
        """Devuelve MOMENTO_1_PLANEACION con fechas de contrato pre-llenadas."""
        s = copy.deepcopy(MOMENTO_1_PLANEACION)

        fill_section(s, "info_ep", "fecha_inicio_ep", aprendiz.fecha_inicio_str())
        fill_section(s, "info_ep", "fecha_fin_ep",    aprendiz.fecha_fin_str())

        return to_json_list(s)

    @staticmethod
    def fill_momento_2() -> list[dict]:
        """Devuelve MOMENTO_2_SEGUIMIENTO vacío (depende de la visita)."""
        return to_json_list(MOMENTO_2_SEGUIMIENTO)

    @staticmethod
    def fill_momento_3() -> list[dict]:
        """Devuelve MOMENTO_3_EVALUACION_COMPLETA vacío."""
        return to_json_list(MOMENTO_3_EVALUACION)
