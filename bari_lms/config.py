ROLE_TO_SLUG = {
    "Administrador": "administrador",
    "Administrativo": "administrativo",
    "Instructor": "instructor",
    "Aprendiz": "aprendiz",
}

AVAILABLE_ROLES = list(ROLE_TO_SLUG.keys())

DEFAULT_USERS = [
    {
        "email": "admin@senalearn.edu.co",
        "password": "Admin123*",
        "role": "Administrador",
        "name": "Laura Moreno",
        "active": 1,
    },
    {
        "email": "administrativo@senalearn.edu.co",
        "password": "Adminvo123*",
        "role": "Administrativo",
        "name": "Carlos Ruiz",
        "active": 1,
    },
    {
        "email": "instructor@senalearn.edu.co",
        "password": "Instructor123*",
        "role": "Instructor",
        "name": "Diana Beltran",
        "active": 1,
    },
    {
        "email": "aprendiz@senalearn.edu.co",
        "password": "Aprendiz123*",
        "role": "Aprendiz",
        "name": "Miguel Torres",
        "active": 1,
    },
]

DEFAULT_LEVELS = [
    "Técnico",
    "Tecnólogo",
    "Operario",
    "Auxiliar",
    "Curso",
]

DASHBOARDS = {
    "administrador": {
        "role": "Administrador",
        "icon": "fa-user-shield",
        "area": "Direccionamiento institucional",
        "title": "Tablero del Administrador",
        "text": "Supervisa la operación general de BARÍ LMS, define lineamientos y controla el acceso de los perfiles del LMS.",
        "footer": "BARÍ LMS SENA - Administrador",
        "menu_heading": "Administración",
        "menu": [
            {"icon": "fa-users-cog", "label": "Usuarios y roles", "endpoint": "admin_users"},
            {"icon": "fa-user-friends", "label": "Gestionar personas", "endpoint": "admin_people"},
            {"icon": "fa-sitemap", "label": "Estructura institucional", "endpoint": "admin_structure"},
            {"icon": "fa-graduation-cap", "label": "Gestión académica", "endpoint": "admin_academic"},
            {
                "icon": "fa-chart-pie",
                "label": "Indicadores",
                "endpoint": "dashboard",
                "endpoint_kwargs": {"role_slug": "administrador"},
            },
        ],
        "metrics": [
            {"label": "Usuarios activos", "value": "0", "icon": "fa-users"},
            {"label": "Regionales", "value": "0", "icon": "fa-map-marked-alt"},
            {"label": "Roles configurados", "value": "0", "icon": "fa-user-shield"},
            {"label": "Centros", "value": "0", "icon": "fa-building"},
        ],
        "tasks_title": "Frentes prioritarios",
        "tasks": [
            {"title": "Gestión de usuarios", "text": "Aprobar nuevas cuentas y validar asignación de perfiles."},
            {"title": "Estructura institucional", "text": "Administrar regionales, centros, coordinaciones, sedes y ambientes."},
            {"title": "Seguimiento", "text": "Consultar indicadores de uso, permanencia y actividad por centro."},
        ],
        "table_title": "Resumen operativo",
        "table_headers": ["Unidad", "Estado", "Observación"],
        "table_rows": [
            ["Regional Distrito Capital", "98%", "Sin novedades"],
            ["Regional Antioquia", "94%", "Actualizar instructores"],
            ["Regional Valle", "91%", "Revisión de permisos"],
        ],
    },
    "administrativo": {
        "role": "Administrativo",
        "icon": "fa-clipboard-check",
        "area": "Apoyo académico y operativo",
        "title": "Tablero Administrativo",
        "text": "Consolida fichas, programas, ambientes y apoyo documental para el despliegue de la formación por proyectos.",
        "footer": "BARÍ LMS SENA - Administrativo",
        "menu_heading": "Operación",
        "menu": [
            {
                "icon": "fa-folder-open",
                "label": "Fichas y programas",
                "endpoint": "dashboard",
                "endpoint_kwargs": {"role_slug": "administrativo"},
            },
            {
                "icon": "fa-school",
                "label": "Ambientes y sedes",
                "endpoint": "dashboard",
                "endpoint_kwargs": {"role_slug": "administrativo"},
            },
        ],
        "metrics": [
            {"label": "Fichas activas", "value": "86", "icon": "fa-id-badge"},
            {"label": "Programas", "value": "27", "icon": "fa-graduation-cap"},
            {"label": "Ambientes", "value": "49", "icon": "fa-door-open"},
            {"label": "Solicitudes", "value": "12", "icon": "fa-clipboard-list"},
        ],
        "tasks_title": "Pendientes",
        "tasks": [
            {"title": "Matrícula", "text": "Consolidar aprendices por ficha y programa."},
            {"title": "Ambientes", "text": "Validar capacidad y disponibilidad por sede."},
            {"title": "Soporte documental", "text": "Publicar formatos y circulares internas."},
        ],
        "table_title": "Control académico",
        "table_headers": ["Ficha", "Programa", "Estado"],
        "table_rows": [
            ["ADSI 2675854", "Análisis y Desarrollo", "Completa"],
            ["SST 2675921", "Seguridad y Salud", "Pendiente soporte"],
            ["Cocina 2676018", "Técnico en Cocina", "Actualizada"],
        ],
    },
    "instructor": {
        "role": "Instructor",
        "icon": "fa-chalkboard-teacher",
        "area": "Ejecución formativa",
        "title": "Tablero del Instructor",
        "text": "Organiza resultados de aprendizaje, evidencias, proyectos y seguimiento del avance de cada ficha.",
        "footer": "BARÍ LMS SENA - Instructor",
        "menu_heading": "Formación",
        "menu": [
            {
                "icon": "fa-layer-group",
                "label": "Mis Fichas",
                "endpoint": "instructor_fichas",
            },
            {
                "icon": "fa-clipboard-check",
                "label": "Evaluación",
                "endpoint": "dashboard",
                "endpoint_kwargs": {"role_slug": "instructor"},
            },
            {
                "icon": "fa-key",
                "label": "Cambiar contraseña",
                "endpoint": "instructor_change_password",
            },
        ],
        "metrics": [
            {"label": "Fichas a cargo", "value": "6", "icon": "fa-layer-group"},
            {"label": "Proyectos activos", "value": "18", "icon": "fa-project-diagram"},
            {"label": "Evidencias por revisar", "value": "43", "icon": "fa-tasks"},
            {"label": "Alertas de asistencia", "value": "5", "icon": "fa-user-clock"},
        ],
        "tasks_title": "Acciones docentes",
        "tasks": [
            {"title": "Planeación", "text": "Programar actividades alineadas al proyecto formativo."},
            {"title": "Seguimiento", "text": "Retroalimentar evidencias y avances semanales."},
            {"title": "Evaluación", "text": "Registrar desempeño por resultado de aprendizaje."},
        ],
        "table_title": "Seguimiento de fichas",
        "table_headers": ["Ficha", "Actividad", "Estado"],
        "table_rows": [
            ["Ficha 2675854", "Sprint de prototipo", "15 entregas pendientes"],
            ["Ficha 2675860", "Sustentación parcial", "Programada"],
            ["Ficha 2675902", "Bitácora de proyecto", "Al día"],
        ],
    },
    "aprendiz": {
        "role": "Aprendiz",
        "icon": "fa-user-graduate",
        "area": "Ruta de aprendizaje",
        "title": "Tablero del Aprendiz",
        "text": "Consulta tu avance del proyecto, entregas, evidencias, horario y comunicados del proceso formativo.",
        "footer": "BARÍ LMS SENA - Aprendiz",
        "menu_heading": "Aprendizaje",
        "menu": [
            {
                "icon": "fa-project-diagram",
                "label": "Mi proyecto",
                "endpoint": "dashboard",
                "endpoint_kwargs": {"role_slug": "aprendiz"},
            },
            {
                "icon": "fa-file-alt",
                "label": "Evidencias",
                "endpoint": "dashboard",
                "endpoint_kwargs": {"role_slug": "aprendiz"},
            },
        ],
        "metrics": [
            {"label": "Avance general", "value": "72%", "icon": "fa-chart-line"},
            {"label": "Evidencias pendientes", "value": "4", "icon": "fa-file-upload"},
            {"label": "Resultados aprobados", "value": "11", "icon": "fa-check-circle"},
            {"label": "Mensajes nuevos", "value": "3", "icon": "fa-comments"},
        ],
        "tasks_title": "Ruta personal",
        "tasks": [
            {"title": "Proyecto formativo", "text": "Consultar entregables y fechas de corte."},
            {"title": "Ruta individual", "text": "Ver resultados alcanzados y faltantes."},
            {"title": "Comunicación", "text": "Revisar mensajes de instructor y coordinación."},
        ],
        "table_title": "Próximas entregas",
        "table_headers": ["Actividad", "Fecha", "Estado"],
        "table_rows": [
            ["Bitácora semanal", "14 de marzo de 2026", "Pendiente"],
            ["Prototipo funcional", "18 de marzo de 2026", "En progreso"],
            ["Autoevaluacion", "20 de marzo de 2026", "No iniciada"],
        ],
    },
}
