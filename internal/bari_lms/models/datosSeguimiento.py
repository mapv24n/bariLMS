from enum import Enum
import copy

class ElementType(Enum):
    GREEN = 2
    BLUE = 3


# 🔧 SIMPLE FIELD WRAPPER (optional use)
def field(value="", ftype="text"):
    return {
        "value": value,
        "type": ftype
    }


# ===============================
# 📄 INFORMACION GENERAL
# ===============================

INFORMACION_GENERAL = {
    "Información general": {
        "Regional": field(""),
        "Centro de formación": field(""),
        "Nivel formativo": field("", "select"),
        "Programa de formación": field("", "select"),
        "No. Grupo": field(""),

        "Modalidad de formación": {
            "Presencial": field(False, "checkbox"),
            "Virtual": field(False, "checkbox"),
            "A distancia": field(False, "checkbox")
        },

        "Estrategia formativa": field(""),
        "Fecha fin de la etapa lectiva": field("", "date")
    },

    "Datos del aprendiz": {
        "Nombre completo": field(""),
        "Tipo de documento": field(""),
        "Número de identificación": field(""),
        "Contacto telefónico": field(""),
        "Dirección": field(""),
        "Correo electrónico personal": field(""),
        "Correo electrónico institucional": field(""),
        "Alternativa de etapa productiva registrada": field(""),
        "Fecha de registro en SofiaPlus": field("", "date")
    },

    "Datos del instructor de seguimiento": {
        "Nombre": field(""),
        "Contacto telefónico": field(""),
        "Correo electrónico institucional": field("")
    },

    "Datos del ente co-formador": {
        "Nombre empresa o entidad co-formadora": field(""),
        "Dirección": field(""),
        "NIT": field(""),
        "Correo electrónico": field(""),
        "Nombre del jefe inmediato o co-formador": field(""),
        "Cargo": field(""),
        "Contacto telefónico": field(""),
        "Nombre otro contacto": field(""),
        "Teléfono institucional (fijo/móvil)": field("")
    },

    "Persona en situación de discapacidad (si aplica)": {
        "Nombre de la persona que asiste al aprendiz": field(""),
        "Tipo de asistencia": field(""),
        "Contacto telefónico": field("")
    }
}


# ===============================
# 📄 MOMENTO 1
# ===============================

MOMENTO_1_PLANEACION = {
    "Información de la Etapa Productiva": {
        "Fecha inicio etapa productiva": field("", "date"),
        "Fecha fin de etapa productiva": field("", "date"),
        "Fecha de afiliación a la ARL": field("", "date"),
        "Número de póliza ARL": field(""),

        "Horario": {
            "Jornada": field(""),
            "Días de la semana": field(""),
            "Hora": field("")
        },

        "Enlace de grabación del momento 1": field("")
    },

    "Concertación plan de trabajo": {
        "Competencias a desarrollar": field(""),
        "Resultados de aprendizaje": field(""),
        "Actividades a desarrollar": field(""),
        "Evidencias de aprendizaje": field(""),
        "Observaciones adicionales": field("")
    },

    "Formalización y firmas": {
        "Firma del aprendiz": field(False, "checkbox"),
        "Firma del instructor de seguimiento": field(False, "checkbox"),
        "Firma del ente co-formador": field(False, "checkbox"),

        "Lugar de diligenciamiento": {
            "Ciudad": field(""),
            "Fecha": field("", "date")
        },

        "Modalidad de diligenciamiento": {
            "Presencial": field(False, "checkbox"),
            "Virtual": field(False, "checkbox")
        }
    }
}


# ===============================
# 📄 MOMENTO 2
# ===============================

def eval_field():
    return {
        "Valoración": field("", "select"),
        "Observaciones": field("")
    }


MOMENTO_2_SEGUIMIENTO = {
    "Información del Seguimiento": {
        "Fecha inicio de etapa productiva": field("", "date"),
        "Fecha del momento de seguimiento": field("", "date"),
        "Modalidad del seguimiento": field("", "select"),
        "Enlace de grabación del momento 2": field("")
    },

    "Factores Técnicos": {
        "Aplicación de conocimiento": eval_field(),
        "Mejora continua": eval_field(),
        "Fortalecimiento ocupacional": eval_field(),
        "Oportunidad y calidad": eval_field(),
        "Responsabilidad ambiental": eval_field(),
        "Administración de recursos": eval_field(),
        "Seguridad y salud en el trabajo": eval_field(),
        "Documentación etapa productiva": eval_field()
    },

    "Factores Actitudinales y Comportamentales": {
        "Relaciones interpersonales": eval_field(),
        "Trabajo en equipo": eval_field(),
        "Solución de problemas": eval_field(),
        "Cumplimiento": eval_field(),  # FIXED typo
        "Organización": eval_field()
    },

    "Observaciones Complementarias": {
        "Observaciones del instructor de seguimiento": field(""),
        "Observaciones del aprendiz": field(""),
        "Observaciones del responsable ente co-formador": field("")
    },

    "Formalización y firmas": {
        "Firma del aprendiz": field(False, "checkbox"),
        "Firma instructor de seguimiento": field(False, "checkbox"),
        "Firma del ente co-formador": field(False, "checkbox"),

        "Lugar de diligenciamiento": {
            "Ciudad": field(""),
            "Fecha": field("", "date")
        },

        "Modalidad de diligenciamiento": {
            "Presencial": field(False, "checkbox"),
            "Virtual": field(False, "checkbox")
        }
    }
}


# ===============================
# 📄 MOMENTO 3 (FIXED STRUCTURE)
# ===============================

MOMENTO_3_EVALUACION_COMPLETA = {
    "Encabezado Evaluación": {
        "Fecha inicio etapa productiva": field("", "date"),
        "Fecha fin ejecución etapa productiva": field("", "date"),
        "Número visitas realizadas": field(0, "number"),
        "Evaluación realizada en forma": field("", "select"),
        "Enlace grabación": field("")
    },

    "Juicio Evaluación Final": {
        "Resultado": field("", "select"),
        "Observaciones": field("")
    },

    "Formalización y Firmas": {
        "Aprendiz": {
            "Firmado": field(False, "checkbox"),
            "Fecha firma": field("", "date"),
            "Ruta firma": field("")
        },
        "Instructor": {
            "Firmado": field(False, "checkbox"),
            "Fecha firma": field("", "date"),
            "Ruta firma": field("")
        }
    }
}


# ===============================
# 🔁 HELPERS (SIMPLE & WORKING)
# ===============================

def is_field(obj):
    return isinstance(obj, dict) and "type" in obj


def load_data(form, data):
    for key, value in form.items():
        if is_field(value):
            if key in data:
                value["value"] = data[key]
        elif isinstance(value, dict):
            load_data(value, data.get(key, {}))


def get_data(form):
    result = {}
    for key, value in form.items():
        if is_field(value):
            result[key] = value["value"]
        elif isinstance(value, dict):
            result[key] = get_data(value)
    return result


def render(form):
    html = ""

    for key, value in form.items():
        if is_field(value):
            t = value["type"]

            if t == "text":
                html += f'<input placeholder="{key}"><br>'

            elif t == "date":
                html += f'<input type="date"><br>'

            elif t == "checkbox":
                html += f'<label><input type="checkbox"> {key}</label><br>'

            elif t == "select":
                html += f'<select><option>{key}</option></select><br>'

        else:
            html += f"<fieldset><legend>{key}</legend>"
            html += render(value)
            html += "</fieldset>"

    return html


def checkFormElement(formElement):
    return isinstance(formElement, dict)


def CheckFormElementType(formElement):
    if checkFormElement(formElement):
        return True
    return False


def clone(form):
    return copy.deepcopy(form)