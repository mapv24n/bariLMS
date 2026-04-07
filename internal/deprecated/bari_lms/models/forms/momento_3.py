"""Formulario: Momento 3 — Evaluación final."""

from bari_lms.models.forms.base import FormField, FormSection


def _eval() -> dict:
    return {"valoracion": "", "observaciones": ""}


MOMENTO_3_EVALUACION: list[FormSection] = [

    FormSection("encabezado_eval", "Encabezado de Evaluación", fields=[
        FormField("fecha_inicio_ep",    "Fecha inicio etapa productiva",           "date"),
        FormField("fecha_fin_ep",       "Fecha fin ejecución etapa productiva",    "date"),
        FormField("num_visitas",        "Número de visitas realizadas",            "number", value=0),
        FormField("modalidad_eval",     "Evaluación realizada en forma",           "select",
                  options=["Presencial", "Virtual"]),
        FormField("enlace_momento_3",   "Enlace de grabación (si es virtual)",     "text"),
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

    FormSection("retroalimentacion", "Retroalimentación", fields=[
        FormField("retro_proceso_coformador",      "Proceso de formación — Ente co-formador",          "textarea"),
        FormField("retro_desempeno_coformador",    "Desempeño competencias — Ente co-formador",        "textarea"),
        FormField("retro_proceso_instructor",      "Proceso de formación — Instructor",                "textarea"),
        FormField("retro_desempeno_instructor",    "Desempeño competencias — Instructor",              "textarea"),
        FormField("retro_proceso_aprendiz",        "Proceso de formación — Aprendiz",                  "textarea"),
        FormField("retro_desempeno_aprendiz",      "Desempeño competencias — Aprendiz",                "textarea"),
    ]),

    FormSection("juicio_final", "Juicio de Evaluación Final", fields=[
        FormField("resultado",      "Resultado",                           "select",
                  options=["Aprobado", "No aprobado"]),
        FormField("observaciones",  "Observaciones del instructor",        "textarea"),
    ]),

    FormSection("formalizacion_3", "Formalización y Firmas", fields=[
        FormField("firma_aprendiz",    "Firma del aprendiz",              "checkbox", value=False),
        FormField("firma_instructor",  "Firma del instructor",            "checkbox", value=False),
        FormField("firma_coformador",  "Firma del ente co-formador",      "checkbox", value=False),
        FormField("ciudad",            "Ciudad",                          "text"),
        FormField("fecha_firma",       "Fecha de diligenciamiento",       "date"),
        FormField("modalidad_firma",   "Modalidad de diligenciamiento",   "checkbox-group",
                  options=["Presencial", "Virtual"],                       value=[]),
    ]),
]
