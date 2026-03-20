"""Blueprint del área de administración."""

from bari_lms.controllers.admin import academico, estructura, personas, usuarios


def register_routes(app):
    usuarios.register_routes(app)
    personas.register_routes(app)
    estructura.register_routes(app)
    academico.register_routes(app)
