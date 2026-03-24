INFORMACION_GENERAL = {
    "Información general": {
        "Regional": "",
        "Centro de formación": "",
        "Nivel formativo": "",
        "Programa de formación": "",
        "No. Grupo": "",
        "Modalidad de formación": {
            "Presencial": False,
            "Virtual": False,
            "A distancia": False
        },
        "Estrategia formativa": "",
        "Fecha fin de la etapa lectiva": ""
    },

    "Datos del aprendiz": {
        "Nombre completo": "",
        "Tipo de documento": "",
        "Número de identificación": "",
        "Contacto telefónico": "",
        "Dirección": "",
        "Correo electrónico personal": "",
        "Correo electrónico institucional": "",
        "Alternativa de etapa productiva registrada": "",
        "Fecha de registro en SofiaPlus": ""
    },

    "Datos del instructor de seguimiento": {
        "Nombre": "",
        "Contacto telefónico": "",
        "Correo electrónico institucional": ""
    },

    "Datos del ente co-formador": {
        "Nombre empresa o entidad co-formadora": "",
        "Dirección": "",
        "NIT": "",
        "Correo electrónico": "",
        "Nombre del jefe inmediato o co-formador": "",
        "Cargo": "",
        "Contacto telefónico": "",
        "Nombre otro contacto": "",
        "Teléfono institucional (fijo/móvil)": ""
    },

    "Persona en situación de discapacidad (si aplica)": {
        "Nombre de la persona que asiste al aprendiz": "",
        "Tipo de asistencia": "",
        "Contacto telefónico": ""
    }
}

MOMENTO_1_PLANEACION = {
    "Información de la Etapa Productiva": {
        "Fecha inicio etapa productiva": "",
        "Fecha fin de etapa productiva": "",
        "Fecha de afiliación a la ARL": "",
        "Número de póliza ARL": "",
        "Horario": {
            "Jornada": "", # Diurno/Nocturno
            "Días de la semana": "",
            "Hora": ""
        },
        "Enlace de grabación del momento 1": ""
    },

    "Concertación plan de trabajo": {
        "Competencias a desarrollar": "",
        "Resultados de aprendizaje": "",
        "Actividades a desarrollar": "",
        "Evidencias de aprendizaje": "",
        "Observaciones adicionales": ""
    },

    "Formalización y firmas": {
        "Firma del aprendiz": False,
        "Firma del instructor de seguimiento": False,
        "Firma del ente co-formador": False,
        "Lugar de diligenciamiento": {
            "Ciudad": "",
            "Fecha": ""
        },
        "Modalidad de diligenciamiento": {
            "Presencial": False,
            "Virtual": False
        }
    }
}

MOMENTO_2_SEGUIMIENTO = {
    "Información del Seguimiento": {
        "Fecha inicio de etapa productiva": "",
        "Fecha del momento de seguimiento": "",
        "Modalidad del seguimiento": "", # Presencial / Virtual
        "Enlace de grabación del momento 2": ""
    },

    "Factores Técnicos": {
        "Aplicación de conocimiento": {"Valoración": "", "Observaciones": ""},
        "Mejora continua": {"Valoración": "", "Observaciones": ""},
        "Fortalecimiento ocupacional": {"Valoración": "", "Observaciones": ""},
        "Oportunidad y calidad": {"Valoración": "", "Observaciones": ""},
        "Responsabilidad ambiental": {"Valoración": "", "Observaciones": ""},
        "Administración de recursos": {"Valoración": "", "Observaciones": ""},
        "Seguridad y salud en el trabajo": {"Valoración": "", "Observaciones": ""},
        "Documentación etapa productiva": {"Valoración": "", "Observaciones": ""}
    },

    "Factores Actitudinales y Comportamentales": {
        "Relaciones interpersonales": {"Valoración": "", "Observaciones": ""},
        "Trabajo en equipo": {"Valoración": "", "Observaciones": ""},
        "Solución de problemas": {"Valoración": "", "Observaciones": ""},
        "Cumplimiento": {"Valorations": "", "Observaciones": ""},
        "Organización": {"Valoración": "", "Observaciones": ""}
    },

    "Observaciones Complementarias": {
        "Observaciones del instructor de seguimiento": "",
        "Observaciones del aprendiz": "",
        "Observaciones del responsable ente co-formador": ""
    },

    "Formalización y firmas": {
        "Firma del aprendiz": None,
        "Firma instructor de seguimiento": None,
        "Firma del ente co-formador": None,
        "Lugar de diligenciamiento": {
            "Ciudad": "",
            "Fecha": ""
        },
        "Modalidad de diligenciamiento": {
            "Presencial": False,
            "Virtual": False
        }
    }
}

MOMENTO_3_EVALUACION_COMPLETA = {
    "Encabezado_Evaluacion": {
        "Fecha_inicio_etapa_productiva": "", # DD/MM/AA
        "Fecha_fin_ejecucion_etapa_productiva": "", # DD/MM/AA
        "Numero_visitas_realizadas_total": 0,
        "Evaluacion_realizada_en_forma": "", # presencial / virtual
        "Enlace_grabacion_momento_3": "" # Solo si es virtual
    },

    "Evaluacion_de_Factores": {
        "Factores_Tecnicos": {
            "Aplicacion_de_conocimiento": {"Valoracion": None, "Observaciones_Compromisos": ""},
            "Mejora_continua": {"Valoracion": None, "Observaciones_Compromisos": ""},
            "Fortalecimiento_ocupacional": {"Valoracion": None, "Observaciones_Compromisos": ""},
            "Oportunidad_y_calidad": {"Valoracion": None, "Observaciones_Compromisos": ""},
            "Responsabilidad_ambiental": {"Valoracion": None, "Observaciones_Compromisos": ""},
            "Administracion_de_recursos": {"Valoracion": None, "Observaciones_Compromisos": ""},
            "Seguridad_y_salud_en_el_trabajo": {"Valoracion": None, "Observaciones_Compromisos": ""},
            "Documentacion_etapa_productiva": {"Valoracion": None, "Observaciones_Compromisos": ""}
        },
        "Factores_Actitudinales_y_Comportamentales": {
            "Relaciones_interpersonales": {"Valoracion": None, "Observaciones_Compromisos": ""},
            "Trabajo_en_equipo": {"Valoracion": None, "Observaciones_Compromisos": ""},
            "Solucion_de_problemas": {"Valoracion": None, "Observaciones_Compromisos": ""},
            "Cumplimiento": {"Valoracion": None, "Observaciones_Compromisos": ""},
            "Organizacion": {"Valoracion": None, "Observaciones_Compromisos": ""}
        }
    },

    "Seccion_Retroalimentacion": {
        "Ente_Co_formador": {
            "Proceso_de_formacion_del_aprendiz": "",
            "Desempeno_competencias_tecnicas_y_actitudinales": ""
        },
        "Instructor_de_Seguimiento": {
            "Proceso_de_formacion_del_aprendiz": "",
            "Desempeno_competencias_tecnicas_y_actitudinales": ""
        },
        "Aprendiz": {
            "Proceso_de_formacion_del_aprendiz": "",
            "Desempeno_competencias_tecnicas_y_actitudinales": ""
        }
    },

    "Juicio_Evaluacion_Final": {
        "Resultado": "", # "Aprobado" o "No aprobado"
        "Observaciones_Instructor_Seguimiento": "" 
    },

    "Formalizacion_y_Firmas": {
        "Firmas": {
            "Aprendiz": {
                "Firmado": False,
                "Fecha_firma": "",
                "Ruta_archivo_firma": "" # Para almacenar la imagen o base64
            },
            "Instructor_de_seguimiento": {
                "Firmado": False,
                "Fecha_firma": "",
                "Ruta_archivo_firma": ""
            },
            "Ente_co_formador": {
                "Firmado": False,
                "Fecha_firma": "",
                "Ruta_archivo_firma": ""
            }
        },
        "Pie_de_Pagina": {
            "Ciudad": "",
            "Fecha_diligenciamiento": "", # DD / MM / AAAA
            "Modalidad_de_diligenciamiento": {
                "Presencial": False,
                "Virtual": False
            }
        }
    }
}