"""Paths de templates del módulo Etapa Productiva — Instructor."""


class PlantillasEPInstructor:
    FICHAS        = "etapa_productiva/instructores.html"
    FICHA_DETALLE = "etapa_productiva/ficha_detalle.html"
    SIN_FICHAS    = "etapa_productiva/novedades/sin_fichas.html"
    SIN_APRENDICES = "etapa_productiva/novedades/sin_aprendices_ep.html"
    SIN_EMPRESAS  = "etapa_productiva/novedades/sin_empresas_ep.html"

    # CU007 — DEPRECATED: formularios dinámicos (ver internal/deprecated/)
    PROCESO       = "etapa_productiva/aprendiz/proceso/proceso.html"

    # Contrato de aprendizaje
    CONTRATO_CREAR   = "etapa_productiva/aprendiz/contrato/contrato_crear.html"
    CONTRATO_EDITAR  = "etapa_productiva/aprendiz/contrato/contrato_editar.html"

    # CU-G — Gestión relacional del proceso EP
    GESTIONAR        = "etapa_productiva/aprendiz/gestionar/gestionar.html"
    EDITAR_MOMENTO_1 = "etapa_productiva/aprendiz/gestionar/editar_momento_1.html"
    EDITAR_MOMENTO_2 = "etapa_productiva/aprendiz/gestionar/editar_momento_2.html"
    EDITAR_MOMENTO_3 = "etapa_productiva/aprendiz/gestionar/editar_momento_3.html"
