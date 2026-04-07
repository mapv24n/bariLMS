"""Formulario: Momento 1 — Planeación."""

from bari_lms.models.forms.base import FormField, FormSection

MOMENTO_1_PLANEACION: list[FormSection] = [

    FormSection("info_ep", "Información de la Etapa Productiva", fields=[
        FormField("fecha_inicio_ep",   "Fecha inicio etapa productiva",  "date"),
        FormField("fecha_fin_ep",      "Fecha fin de etapa productiva",  "date"),
        FormField("fecha_arl",         "Fecha de afiliación a la ARL",   "date"),
        FormField("poliza_arl",        "Número de póliza ARL",           "text"),
        FormField("horario_jornada",   "Jornada",                        "text"),
        FormField("horario_dias",      "Días de la semana",              "text"),
        FormField("horario_hora",      "Hora",                           "text"),
        FormField("enlace_momento_1",  "Enlace de grabación del momento 1", "text"),
    ]),

    FormSection("plan_trabajo", "Concertación plan de trabajo", fields=[
        FormField("competencias",      "Competencias a desarrollar",     "textarea"),
        FormField("resultados",        "Resultados de aprendizaje",      "textarea"),
        FormField("actividades",       "Actividades a desarrollar",      "textarea"),
        FormField("evidencias",        "Evidencias de aprendizaje",      "textarea"),
        FormField("observaciones",     "Observaciones adicionales",      "textarea"),
    ]),

    FormSection("formalizacion_1", "Formalización y firmas", fields=[
        FormField("firma_aprendiz",    "Firma del aprendiz",             "checkbox", value=False),
        FormField("firma_instructor",  "Firma del instructor de seguimiento", "checkbox", value=False),
        FormField("firma_coformador",  "Firma del ente co-formador",     "checkbox", value=False),
        FormField("ciudad",            "Ciudad",                         "text"),
        FormField("fecha_firma",       "Fecha",                          "date"),
        FormField("modalidad_firma",   "Modalidad de diligenciamiento",  "checkbox-group",
                  options=["Presencial", "Virtual"],                     value=[]),
    ]),
]
