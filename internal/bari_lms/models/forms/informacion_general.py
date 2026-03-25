"""Formulario: Información General (momento 0 — datos base del proceso EP)."""

from bari_lms.models.forms.base import FormField, FormSection

INFORMACION_GENERAL: list[FormSection] = [

    FormSection("informacion_general", "Información general", fields=[
        FormField("regional",            "Regional",                        "text"),
        FormField("centro_formacion",    "Centro de formación",             "text"),
        FormField("nivel_formativo",     "Nivel formativo",                 "text"),
        FormField("programa_formacion",  "Programa de formación",           "text"),
        FormField("no_grupo",            "No. Grupo",                       "text"),
        FormField("modalidad_formacion", "Modalidad de formación",          "checkbox-group",
                  options=["Presencial", "Virtual", "A distancia"],        value=[]),
        FormField("estrategia",          "Estrategia formativa",            "text"),
        FormField("fecha_fin_lectiva",   "Fecha fin de la etapa lectiva",   "date"),
    ]),

    FormSection("datos_aprendiz", "Datos del aprendiz", fields=[
        FormField("nombre_completo",       "Nombre completo",                        "text"),
        FormField("tipo_documento",        "Tipo de documento",                      "text"),
        FormField("numero_documento",      "Número de identificación",               "text"),
        FormField("telefono",              "Contacto telefónico",                    "tel"),
        FormField("direccion",             "Dirección",                              "text"),
        FormField("correo_personal",       "Correo electrónico personal",            "email"),
        FormField("correo_institucional",  "Correo electrónico institucional",       "email"),
        FormField("alternativa_ep",        "Alternativa de EP registrada",           "text"),
        FormField("fecha_sofia",           "Fecha de registro en SofiaPlus",         "date"),
    ]),

    FormSection("datos_instructor", "Datos del instructor de seguimiento", fields=[
        FormField("instructor_nombre",  "Nombre",                          "text"),
        FormField("instructor_telefono","Contacto telefónico",             "tel"),
        FormField("instructor_correo",  "Correo electrónico institucional","email"),
    ]),

    FormSection("datos_empresa", "Datos del ente co-formador", fields=[
        FormField("empresa_nombre",     "Nombre empresa o entidad co-formadora",    "text"),
        FormField("empresa_direccion",  "Dirección",                                "text"),
        FormField("empresa_nit",        "NIT",                                      "text"),
        FormField("empresa_correo",     "Correo electrónico",                       "email"),
        FormField("jefe_nombre",        "Nombre del jefe inmediato o co-formador",  "text"),
        FormField("jefe_cargo",         "Cargo",                                    "text"),
        FormField("empresa_telefono",   "Contacto telefónico",                      "tel"),
        FormField("otro_contacto",      "Nombre otro contacto",                     "text"),
        FormField("telefono_fijo",      "Teléfono institucional (fijo/móvil)",      "tel"),
    ]),

    FormSection("discapacidad", "Persona en situación de discapacidad (si aplica)", fields=[
        FormField("discapacidad_asistente", "Nombre de la persona que asiste al aprendiz", "text"),
        FormField("discapacidad_tipo",      "Tipo de asistencia",                          "text"),
        FormField("discapacidad_telefono",  "Contacto telefónico",                         "tel"),
    ]),
]
