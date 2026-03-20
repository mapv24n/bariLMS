"""Blueprint del área de instructor."""

from bari_lms.controllers.instructor import actividades, fichas, perfil


def register_routes(app):
    perfil.register_routes(app)
    fichas.register_routes(app)
    actividades.register_routes(app)
