"""Controlador instructor — Registro de todas las rutas de actividades.

Este módulo actúa como punto de entrada único: delega en submódulos
especializados para mantener cada dominio en su propio archivo.
"""

from bari_lms.controllers.instructor import (
    asistencia,
    evidencias,
    fases,
    guias,
    secciones,
    tree,
)


def register_routes(app):
    tree.register_routes(app)
    guias.register_routes(app)
    evidencias.register_routes(app)
    fases.register_routes(app)
    secciones.register_routes(app)
    asistencia.register_routes(app)
