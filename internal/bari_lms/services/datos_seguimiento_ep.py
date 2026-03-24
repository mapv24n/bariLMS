"""Servicio de formularios EP — llena las plantillas de datos con info real de BD.

Importa las plantillas de datosSeguimiento.py (dicts con campos vacíos) y
devuelve copias profundas pre-llenadas con la información del aprendiz,
instructor y ficha recuperada de la BD.

Uso en la ruta:
    from bari_lms.services.datos_seguimiento_ep import DatosSeguimientoEP
    form_ig = DatosSeguimientoEP.fill_informacion_general(
        aprendiz, instructor_nombre, instructor_correo,
        nivel=ficha["nivel_nombre"], programa=ficha["programa_nombre"],
        ficha_numero=ficha["numero"], centro=instructor_centro,
    )
    # Serializar para el template:
    import json
    form_ig_json = json.dumps(form_ig, ensure_ascii=False)
"""

import copy

from bari_lms.models.datosSeguimiento import (
    INFORMACION_GENERAL,
    MOMENTO_1_PLANEACION,
    MOMENTO_2_SEGUIMIENTO,
    MOMENTO_3_EVALUACION_COMPLETA,
)
from bari_lms.models.aprendiz import Aprendiz


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
    ) -> dict:
        """Devuelve INFORMACION_GENERAL pre-llenado con los datos del aprendiz.

        Todos los campos siguen siendo editables en el formulario — este método
        solo establece valores iniciales. Los campos que no tienen dato en BD
        quedan como cadena vacía (el JS los renderizará como inputs vacíos).
        """
        data = copy.deepcopy(INFORMACION_GENERAL)

        # ── Información general (de la ficha) ─────────────────────────────
        ig = data["Información general"]
        ig["Regional"] = regional or aprendiz.regional or ""
        ig["Centro de formación"] = centro or ""
        ig["Nivel formativo"] = nivel or ""
        ig["Programa de formación"] = programa or ""
        ig["No. Grupo"] = ficha_numero or ""

        # ── Datos del aprendiz ────────────────────────────────────────────
        ap = data["Datos del aprendiz"]
        ap["Nombre completo"] = aprendiz.nombre_completo
        ap["Tipo de documento"] = aprendiz.tipo_documento or ""
        ap["Número de identificación"] = aprendiz.numero_documento or ""
        ap["Correo electrónico personal"] = aprendiz.correo_personal or ""

        # ── Datos del instructor de seguimiento ───────────────────────────
        inst = data["Datos del instructor de seguimiento"]
        inst["Nombre"] = instructor_nombre or ""
        inst["Correo electrónico institucional"] = instructor_correo or ""

        # ── Datos del ente co-formador ────────────────────────────────────
        co = data["Datos del ente co-formador"]
        co["Nombre empresa o entidad co-formadora"] = aprendiz.empresa_nombre or ""
        co["NIT"] = aprendiz.empresa_nit or ""
        co["Correo electrónico"] = aprendiz.empresa_correo or ""
        co["Contacto telefónico"] = aprendiz.empresa_telefono or ""
        co["Dirección"] = aprendiz.empresa_direccion or ""

        return data

    @staticmethod
    def fill_momento_1(aprendiz: Aprendiz) -> dict:
        """Devuelve MOMENTO_1_PLANEACION con las fechas de contrato pre-llenadas."""
        data = copy.deepcopy(MOMENTO_1_PLANEACION)

        ep_info = data["Información de la Etapa Productiva"]
        ep_info["Fecha inicio etapa productiva"] = aprendiz.fecha_inicio_str()
        ep_info["Fecha fin de etapa productiva"] = aprendiz.fecha_fin_str()

        return data

    @staticmethod
    def fill_momento_2() -> dict:
        """Devuelve MOMENTO_2_SEGUIMIENTO vacío (sin pre-llenado, depende de la visita)."""
        return copy.deepcopy(MOMENTO_2_SEGUIMIENTO)

    @staticmethod
    def fill_momento_3() -> dict:
        """Devuelve MOMENTO_3_EVALUACION_COMPLETA vacío."""
        return copy.deepcopy(MOMENTO_3_EVALUACION_COMPLETA)
