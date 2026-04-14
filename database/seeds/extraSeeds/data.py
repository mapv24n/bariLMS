"""
data.py — All seed data in one place.

To expand the dataset, add rows here — seed logic files never need to change.
"""

import uuid


def generate_id():
    """Time-ordered UUID v7 — ideal for sequential DB primary keys."""
    return str(uuid.uuid7())


SEED_PASSWORD = "Sena2024*"

# ── Catalogs ───────────────────────────────────────────────────────────────────
# (codigo, nombre)
DATA_TIPO_DOCUMENTO = [
    ("cc", "Cédula de Ciudadanía"),
    ("ti", "Tarjeta de Identidad"),
    ("ce", "Cédula de Extranjería"),
    ("pp", "Pasaporte"),
]

# (codigo, nombre)
DATA_SEXO = [
    ("m", "Masculino"),
    ("f", "Femenino"),
]

# (nombre,)
DATA_NIVELES_FORMACION = [
    ("Tecnólogo",),
    ("Auxiliar",),
    ("Técnico",),
]

# ── Institutional Structure ────────────────────────────────────────────────────
# (nombre,)
DATA_REGIONALES = [
    ("Regional Norte de Santander",),
]

# (regional_nombre, centro_nombre)
DATA_CENTROS = [
    (
        "Regional Norte de Santander",
        "Centro de Gestión de Mercados, Logística y TIC del Norte de Santander",
    ),
]

# (centro_nombre, coordinacion_nombre)
DATA_COORDINACIONES = [
    (
        "Centro de Gestión de Mercados, Logística y TIC del Norte de Santander",
        "Coordinación de Tecnologías de la Información",
    ),
]

# ── Knowledge Network & Areas ──────────────────────────────────────────────────
# (nombre,)
DATA_REDES = [
    ("Tecnología de la Información y las Comunicaciones",),
]

# (red_nombre, area_nombre)
DATA_AREAS = [
    (
        "Tecnología de la Información y las Comunicaciones",
        "Análisis y Desarrollo de Software",
    ),
]

# (area_nombre, nivel_nombre, programa_nombre)
DATA_PROGRAMAS = [
    ("Análisis y Desarrollo de Software", "Tecnólogo", "Análisis y Desarrollo de Software"),
]

# ── Formative Projects & Phases ────────────────────────────────────────────────
# (codigo, nombre)
DATA_PROYECTOS = [
    ("PF-ADSO-001", "Sistema Integrado de Gestión de Aprendizaje (SIGA)"),
]

# (proyecto_codigo, fase_nombre)
DATA_FASES = [
    ("PF-ADSO-001", "Análisis y Levantamiento de Requisitos"),
    ("PF-ADSO-001", "Diseño de Solución"),
    ("PF-ADSO-001", "Implementación"),
    ("PF-ADSO-001", "Pruebas y Despliegue"),
]

# ── Instructors ────────────────────────────────────────────────────────────────
# (correo, nombre_completo, numero_documento, tipo_doc_codigo,
#  nombres, apellidos, sexo_codigo, ficha_numero)
DATA_INSTRUCTORES = [
    # Original set — fichas 2900001–2900003
    (
        "juan.perez@sena.edu.co",
        "Juan Carlos Pérez Martínez",
        "10254871", "cc",
        "JUAN CARLOS", "PÉREZ MARTÍNEZ",
        "m", "2900001",
    ),
    (
        "maria.lopez@sena.edu.co",
        "María Fernanda López Díaz",
        "37584296", "cc",
        "MARÍA FERNANDA", "LÓPEZ DÍAZ",
        "f", "2900002",
    ),
    (
        "carlos.rodriguez@sena.edu.co",
        "Carlos Alberto Rodríguez Gómez",
        "91345678", "cc",
        "CARLOS ALBERTO", "RODRÍGUEZ GÓMEZ",
        "m", "2900003",
    ),
    # Extra fichas for juan.perez — 2900007, 2900008, 2900009
    (
        "juan.perez@sena.edu.co",
        "Juan Carlos Pérez Martínez",
        "10254871", "cc",
        "JUAN CARLOS", "PÉREZ MARTÍNEZ",
        "m", "2900007",
    ),
    (
        "juan.perez@sena.edu.co",
        "Juan Carlos Pérez Martínez",
        "10254871", "cc",
        "JUAN CARLOS", "PÉREZ MARTÍNEZ",
        "m", "2900008",
    ),
    (
        "juan.perez@sena.edu.co",
        "Juan Carlos Pérez Martínez",
        "10254871", "cc",
        "JUAN CARLOS", "PÉREZ MARTÍNEZ",
        "m", "2900009",
    ),
    # Extended set — fichas 2900004–2900006
    (
        "adriana.suarez@sena.edu.co",
        "Adriana Lucía Suárez Torres",
        "10987654", "cc",
        "ADRIANA LUCÍA", "SUÁREZ TORRES",
        "f", "2900004",
    ),
    (
        "ricardo.mendoza@sena.edu.co",
        "Ricardo Antonio Mendoza Villa",
        "88234567", "cc",
        "RICARDO ANTONIO", "MENDOZA VILLA",
        "m", "2900005",
    ),
    (
        "elena.beltran@sena.edu.co",
        "Elena Patricia Beltrán Ruiz",
        "60332119", "cc",
        "ELENA PATRICIA", "BELTRÁN RUIZ",
        "f", "2900006",
    ),
]

# ── Companies ──────────────────────────────────────────────────────────────────
# (razon_social, nit, sector, correo, telefono)
DATA_EMPRESAS = [
    ("TechSoft SAS",            "9005123456", "Tecnología",      "contacto@techsoft.com.co", "6075551234"),
    ("Innovatech Ltda",         "8002345678", "Consultoría TIC", "info@innovatech.com.co",   "6075559876"),
    ("Sistemas Globales E.U.",  "9019876543", "Software",        "admin@sglobales.com",       "6075710011"),
    ("Logística del Norte SAS", "8901122334", "Logística",       "rrhh@logisnorte.co",        "6075822233"),
]

# ── Apprentices ────────────────────────────────────────────────────────────────
# (correo, nombre_completo, numero_documento, tipo_doc_codigo,
#  nombres, apellidos, sexo_codigo, ficha_numero, estado_formacion)
DATA_APRENDICES = [
    # ── Ficha 2900001 (Juan Pérez) ────────────────────────────────────────────
    ("ana.gomez@aprendiz.sena.edu.co",    "Ana Sofía Gómez Herrera",        "1090123456", "cc", "ANA SOFÍA",       "GÓMEZ HERRERA",    "f", "2900001", "lectiva_en_curso"),
    ("luis.torres@aprendiz.sena.edu.co",  "Luis Eduardo Torres Prado",      "1090234567", "cc", "LUIS EDUARDO",    "TORRES PRADO",     "m", "2900001", "productiva_en_curso"),
    ("mateo.julian@aprendiz.sena.edu.co",  "Mateo Julian Paez Paez",      "1098765456", "cc", "MATEO JULIAN",    "PAEZ PAEZ",     "m", "2900001", "productiva_en_curso"),
    # ── Ficha 2900002 (María López) ───────────────────────────────────────────
    ("sofia.mendez@aprendiz.sena.edu.co", "Sofía Alejandra Méndez Ríos",    "1025345678", "ti", "SOFÍA ALEJANDRA", "MÉNDEZ RÍOS",      "f", "2900002", "lectiva_en_curso"),
    ("andres.ruiz@aprendiz.sena.edu.co",  "Andrés Felipe Ruiz Castillo",    "1025456789", "ti", "ANDRÉS FELIPE",   "RUIZ CASTILLO",    "m", "2900002", "productiva_en_curso"),
    # ── Ficha 2900003 (Carlos Rodríguez) ──────────────────────────────────────
    ("camila.vargas@aprendiz.sena.edu.co","Camila Andrea Vargas Soto",       "1090567890", "cc", "CAMILA ANDREA",   "VARGAS SOTO",      "f", "2900003", "lectiva_en_curso"),
    ("miguel.castro@aprendiz.sena.edu.co","Miguel Ángel Castro Jiménez",     "1090678901", "cc", "MIGUEL ÁNGEL",    "CASTRO JIMÉNEZ",   "m", "2900003", "lectiva_concluida"),
    # ── Ficha 2900004 (Adriana Suárez) ────────────────────────────────────────
    ("mario.duarte@aprendiz.sena.edu.co", "Mario Alberto Duarte Casadiego", "1090888777", "cc", "MARIO ALBERTO",   "DUARTE CASADIEGO", "m", "2900004", "lectiva_en_curso"),
    ("claudia.nieto@aprendiz.sena.edu.co","Claudia Marcela Nieto Rojas",     "1090999111", "cc", "CLAUDIA MARCELA", "NIETO ROJAS",      "f", "2900004", "productiva_en_curso"),
    # ── Ficha 2900005 (Ricardo Mendoza) ───────────────────────────────────────
    ("felipe.basto@aprendiz.sena.edu.co", "Felipe Andres Basto Leon",       "1025777888", "ti", "FELIPE ANDRES",   "BASTO LEON",       "m", "2900005", "lectiva_en_curso"),
    ("paola.ortiz@aprendiz.sena.edu.co",  "Paola Andrea Ortiz Guerrero",    "1025666555", "ti", "PAOLA ANDREA",    "ORTIZ GUERRERO",   "f", "2900005", "productiva_en_curso"),
    # ── Ficha 2900006 (Elena Beltrán) ─────────────────────────────────────────
    ("jorge.vivas@aprendiz.sena.edu.co",  "Jorge Luis Vivas Mendez",        "1090444333", "cc", "JORGE LUIS",      "VIVAS MENDEZ",     "m", "2900006", "lectiva_en_curso"),
    ("diana.solano@aprendiz.sena.edu.co", "Diana Karime Solano Parra",      "1090222888", "cc", "DIANA KARIME",    "SOLANO PARRA",     "f", "2900006", "lectiva_concluida"),
    # ── Ficha 2900007 (Juan Pérez — extra ficha 1) ────────────────────────────
    ("valentina.rios@aprendiz.sena.edu.co",    "Valentina Ríos Castañeda",       "1091100001", "cc", "VALENTINA",       "RÍOS CASTAÑEDA",   "f", "2900007", "productiva_en_curso"),
    ("samuel.guerrero@aprendiz.sena.edu.co",   "Samuel Guerrero Peña",           "1091100002", "cc", "SAMUEL",          "GUERRERO PEÑA",    "m", "2900007", "productiva_en_curso"),
    ("isabella.mora@aprendiz.sena.edu.co",     "Isabella Mora Quintero",         "1091100003", "cc", "ISABELLA",        "MORA QUINTERO",    "f", "2900007", "productiva_en_curso"),
    ("david.pineda@aprendiz.sena.edu.co",      "David Pineda Serrano",           "1091100004", "cc", "DAVID",           "PINEDA SERRANO",   "m", "2900007", "productiva_en_curso"),
    ("laura.espinosa@aprendiz.sena.edu.co",    "Laura Espinosa Rangel",          "1091100005", "cc", "LAURA",           "ESPINOSA RANGEL",  "f", "2900007", "productiva_en_curso"),
    # ── Ficha 2900008 (Juan Pérez — extra ficha 2) ────────────────────────────
    ("nicolas.herrera@aprendiz.sena.edu.co",   "Nicolás Herrera Acosta",         "1091200001", "cc", "NICOLÁS",         "HERRERA ACOSTA",   "m", "2900008", "productiva_en_curso"),
    ("maria.gonzalez@aprendiz.sena.edu.co",    "María Camila González Leal",     "1091200002", "cc", "MARÍA CAMILA",    "GONZÁLEZ LEAL",    "f", "2900008", "productiva_en_curso"),
    ("sebastian.ramirez@aprendiz.sena.edu.co", "Sebastián Ramírez Cárdenas",     "1091200003", "cc", "SEBASTIÁN",       "RAMÍREZ CÁRDENAS", "m", "2900008", "productiva_en_curso"),
    ("juliana.cardenas@aprendiz.sena.edu.co",  "Juliana Cárdenas Medina",        "1091200004", "cc", "JULIANA",         "CÁRDENAS MEDINA",  "f", "2900008", "productiva_en_curso"),
    ("andres.mora@aprendiz.sena.edu.co",       "Andrés Mora Salcedo",            "1091200005", "cc", "ANDRÉS",          "MORA SALCEDO",     "m", "2900008", "productiva_en_curso"),
    # ── Ficha 2900009 (Juan Pérez — extra ficha 3) ────────────────────────────
    ("camilo.suarez@aprendiz.sena.edu.co",     "Camilo Suárez Bohórquez",        "1091300001", "cc", "CAMILO",          "SUÁREZ BOHÓRQUEZ", "m", "2900009", "productiva_en_curso"),
    ("paula.mendez@aprendiz.sena.edu.co",      "Paula Méndez Fonseca",           "1091300002", "cc", "PAULA",           "MÉNDEZ FONSECA",   "f", "2900009", "productiva_en_curso"),
    ("santiago.lopez@aprendiz.sena.edu.co",    "Santiago López Navarro",         "1091300003", "cc", "SANTIAGO",        "LÓPEZ NAVARRO",    "m", "2900009", "productiva_en_curso"),
    ("sara.rodriguez@aprendiz.sena.edu.co",    "Sara Rodríguez Patiño",          "1091300004", "cc", "SARA",            "RODRÍGUEZ PATIÑO", "f", "2900009", "productiva_en_curso"),
    ("juan.david@aprendiz.sena.edu.co",        "Juan David Arenas Villamizar",   "1091300005", "cc", "JUAN DAVID",      "ARENAS VILLAMIZAR","m", "2900009", "productiva_en_curso"),
]

# ── Actividades de Proyecto ────────────────────────────────────────────────────
# One activity per fase — shared across all fichas (same proyecto_formativo).
# (fase_nombre, actividad_nombre, creado_por_correo)
DATA_ACTIVIDADES_PROYECTO = [
    ("Análisis y Levantamiento de Requisitos", "Levantamiento de Requisitos Funcionales", "juan.perez@sena.edu.co"),
    ("Análisis y Levantamiento de Requisitos", "Modelado de Casos de Uso",                "juan.perez@sena.edu.co"),
    ("Diseño de Solución",                     "Diseño de Base de Datos",                 "maria.lopez@sena.edu.co"),
    ("Diseño de Solución",                     "Diseño de Interfaces de Usuario",          "maria.lopez@sena.edu.co"),
    ("Implementación",                         "Desarrollo de Backend",                   "carlos.rodriguez@sena.edu.co"),
    ("Implementación",                         "Desarrollo de Frontend",                  "carlos.rodriguez@sena.edu.co"),
    ("Pruebas y Despliegue",                   "Plan de Pruebas",                         "adriana.suarez@sena.edu.co"),
    ("Pruebas y Despliegue",                   "Despliegue en Producción",                "adriana.suarez@sena.edu.co"),
]

# ── Actividades de Aprendizaje ─────────────────────────────────────────────────
# (actividad_proyecto_nombre, nombre, descripcion, fecha_inicio, fecha_fin, orden)
DATA_ACTIVIDADES_APRENDIZAJE = [
    # ── Levantamiento de Requisitos Funcionales ────────────────────────────────
    ("Levantamiento de Requisitos Funcionales", "Entrevistas con Stakeholders",
     "Realizar entrevistas con los usuarios finales para identificar necesidades del sistema.",
     "2025-02-01", "2025-02-15", 0),
    ("Levantamiento de Requisitos Funcionales", "Documentación de Requisitos",
     "Redactar el documento de especificación de requisitos de software (ERS).",
     "2025-02-16", "2025-02-28", 1),
    # ── Modelado de Casos de Uso ───────────────────────────────────────────────
    ("Modelado de Casos de Uso", "Identificación de Actores y Roles",
     "Identificar los actores del sistema y definir sus roles y responsabilidades.",
     "2025-03-01", "2025-03-10", 0),
    ("Modelado de Casos de Uso", "Elaboración de Diagramas UML",
     "Construir diagramas de casos de uso utilizando notación UML.",
     "2025-03-11", "2025-03-25", 1),
    # ── Diseño de Base de Datos ────────────────────────────────────────────────
    ("Diseño de Base de Datos", "Modelo Entidad-Relación",
     "Diseñar el modelo ER de la aplicación incluyendo todas las entidades y relaciones.",
     "2025-03-01", "2025-03-15", 0),
    ("Diseño de Base de Datos", "Normalización y Scripts DDL",
     "Aplicar normalización hasta 3FN y generar los scripts DDL de creación.",
     "2025-03-16", "2025-03-31", 1),
    # ── Diseño de Interfaces de Usuario ───────────────────────────────────────
    ("Diseño de Interfaces de Usuario", "Wireframes de Pantallas Principales",
     "Crear wireframes de las pantallas principales del sistema.",
     "2025-04-01", "2025-04-15", 0),
    ("Diseño de Interfaces de Usuario", "Prototipo Interactivo en Figma",
     "Desarrollar un prototipo navegable en Figma con los flujos principales.",
     "2025-04-16", "2025-04-30", 1),
    # ── Desarrollo de Backend ──────────────────────────────────────────────────
    ("Desarrollo de Backend", "Configuración del Proyecto y Entorno",
     "Configurar el entorno de desarrollo Flask, estructura de carpetas y dependencias.",
     "2025-04-01", "2025-04-10", 0),
    ("Desarrollo de Backend", "Implementación de APIs REST",
     "Desarrollar los endpoints REST para los módulos principales del sistema.",
     "2025-04-11", "2025-05-15", 1),
    # ── Desarrollo de Frontend ─────────────────────────────────────────────────
    ("Desarrollo de Frontend", "Maquetación HTML/CSS",
     "Implementar las interfaces diseñadas en HTML semántico y CSS.",
     "2025-04-01", "2025-04-20", 0),
    ("Desarrollo de Frontend", "Integración con APIs REST",
     "Conectar el frontend con los endpoints del backend mediante fetch/axios.",
     "2025-04-21", "2025-05-15", 1),
    # ── Plan de Pruebas ────────────────────────────────────────────────────────
    ("Plan de Pruebas", "Casos de Prueba Unitaria",
     "Definir y ejecutar casos de prueba unitaria para los módulos críticos.",
     "2025-05-16", "2025-05-31", 0),
    ("Plan de Pruebas", "Pruebas de Integración",
     "Verificar la correcta integración entre los distintos módulos del sistema.",
     "2025-06-01", "2025-06-15", 1),
    # ── Despliegue en Producción ───────────────────────────────────────────────
    ("Despliegue en Producción", "Configuración del Servidor",
     "Preparar y configurar el servidor de producción.",
     "2025-06-16", "2025-06-25", 0),
    ("Despliegue en Producción", "Lanzamiento y Monitoreo",
     "Desplegar la aplicación y configurar herramientas de monitoreo.",
     "2025-06-26", "2025-06-30", 1),
]

# ── Secciones de Actividad ─────────────────────────────────────────────────────
# (actividad_aprendizaje_nombre, seccion_nombre, descripcion, orden)
DATA_SECCIONES = [
    ("Entrevistas con Stakeholders",   "Guía de Preguntas",          "Listado de preguntas para las entrevistas.",            0),
    ("Documentación de Requisitos",    "Plantilla ERS",              "Plantilla base para el documento ERS.",                 0),
    ("Identificación de Actores y Roles", "Matriz de Roles",         "Tabla de actores con descripción de cada rol.",         0),
    ("Elaboración de Diagramas UML",   "Recursos UML",               "Material de referencia para notación UML.",             0),
    ("Modelo Entidad-Relación",        "Herramientas de Modelado",   "Instrucciones para usar draw.io o DBDesigner.",         0),
    ("Normalización y Scripts DDL",    "Guía de Normalización",      "Resumen de las formas normales con ejemplos.",          0),
    ("Wireframes de Pantallas Principales", "Criterios de Diseño",   "Lineamientos de UX/UI a seguir en los wireframes.",     0),
    ("Prototipo Interactivo en Figma", "Tutorial Figma",             "Guía básica de uso de Figma para prototipos.",          0),
    ("Configuración del Proyecto y Entorno", "Checklist de Setup",   "Lista de verificación para el setup del entorno.",      0),
    ("Implementación de APIs REST",    "Estándares REST",            "Convenciones de nombres y formatos de respuesta.",      0),
    ("Maquetación HTML/CSS",           "Guía de Estilos",            "Variables CSS y componentes base del proyecto.",        0),
    ("Integración con APIs REST",      "Manejo de Errores",          "Patrones recomendados para manejo de errores HTTP.",    0),
    ("Casos de Prueba Unitaria",       "Plantilla de Casos de Prueba","Formato estándar para documentar casos de prueba.",    0),
    ("Pruebas de Integración",         "Checklist de Integración",   "Puntos de verificación entre módulos.",                 0),
    ("Configuración del Servidor",     "Guía de Despliegue",         "Pasos detallados para despliegue en servidor Linux.",   0),
    ("Lanzamiento y Monitoreo",        "Herramientas de Monitoreo",  "Configuración de logs y alertas básicas.",              0),
]
