"""Formulario: Momento 2 — Seguimiento."""

from bari_lms.models.forms.base import FormField, FormSection


def _eval() -> dict:
    """Valor por defecto para un campo de tipo eval-pair."""
    return {"valoracion": "", "observaciones": ""}


MOMENTO_2_SEGUIMIENTO: list[FormSection] = [

    FormSection("info_seguimiento", "Información del Seguimiento", fields=[
        FormField("fecha_inicio_ep",       "Fecha inicio de etapa productiva",    "date"),
        FormField("fecha_momento",         "Fecha del momento de seguimiento",    "date"),
        FormField("modalidad_seguimiento", "Modalidad del seguimiento",           "select",
                  options=["Presencial", "Virtual"]),
        FormField("enlace_momento_2",      "Enlace de grabación del momento 2",   "text"),
    ]),

    FormSection("factores_tecnicos", "Factores Técnicos", fields=[
        FormField("aplicacion_conocimiento",    "Aplicación de conocimiento",          "eval-pair", value=_eval()),
        FormField("mejora_continua",            "Mejora continua",                     "eval-pair", value=_eval()),
        FormField("fortalecimiento_ocupacional","Fortalecimiento ocupacional",          "eval-pair", value=_eval()),
        FormField("oportunidad_calidad",        "Oportunidad y calidad",               "eval-pair", value=_eval()),
        FormField("responsabilidad_ambiental",  "Responsabilidad ambiental",           "eval-pair", value=_eval()),
        FormField("administracion_recursos",    "Administración de recursos",          "eval-pair", value=_eval()),
        FormField("sst",                        "Seguridad y salud en el trabajo",     "eval-pair", value=_eval()),
        FormField("documentacion_ep",           "Documentación etapa productiva",      "eval-pair", value=_eval()),
    ]),

    FormSection("factores_actitudinales", "Factores Actitudinales y Comportamentales", fields=[
        FormField("relaciones_interpersonales", "Relaciones interpersonales",  "eval-pair", value=_eval()),
        FormField("trabajo_equipo",             "Trabajo en equipo",           "eval-pair", value=_eval()),
        FormField("solucion_problemas",         "Solución de problemas",       "eval-pair", value=_eval()),
        FormField("cumplimiento",               "Cumplimiento",                "eval-pair", value=_eval()),
        FormField("organizacion",               "Organización",                "eval-pair", value=_eval()),
    ]),

    FormSection("observaciones_complementarias", "Observaciones Complementarias", fields=[
        FormField("obs_instructor",  "Observaciones del instructor de seguimiento",      "textarea"),
        FormField("obs_aprendiz",    "Observaciones del aprendiz",                       "textarea"),
        FormField("obs_coformador",  "Observaciones del responsable ente co-formador",   "textarea"),
    ]),

    FormSection("formalizacion_2", "Formalización y firmas", fields=[
        FormField("firma_aprendiz",   "Firma del aprendiz",                  "checkbox", value=False),
        FormField("firma_instructor", "Firma del instructor de seguimiento", "checkbox", value=False),
        FormField("firma_coformador", "Firma del ente co-formador",          "checkbox", value=False),
        FormField("ciudad",           "Ciudad",                              "text"),
        FormField("fecha_firma",      "Fecha",                               "date"),
        FormField("modalidad_firma",  "Modalidad de diligenciamiento",       "checkbox-group",
                  options=["Presencial", "Virtual"],                         value=[]),
    ]),
]
