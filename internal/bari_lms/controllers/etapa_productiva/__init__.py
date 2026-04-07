"""Blueprint del módulo de Etapa Productiva."""

from bari_lms.controllers.etapa_productiva import index, instructores, proceso_ep


def register_routes(app):
    index.register_routes(app)
    instructores.register_routes(app)
    proceso_ep.register_routes(app)
