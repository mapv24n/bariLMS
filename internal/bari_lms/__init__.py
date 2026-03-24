import os

from flask import Flask

from bari_lms.controllers.admin import register_routes as register_admin_routes
from bari_lms.controllers.auth import register_routes as register_auth_routes
from bari_lms.controllers.dashboard import register_routes as register_dashboard_routes
from bari_lms.controllers.etapa_productiva import register_routes as register_etapa_productiva_routes
from bari_lms.controllers.instructor import register_routes as register_instructor_routes
from bari_lms.db import close_db, create_pool
from bari_lms.db.bootstrap import initialize_database
from bari_lms.middleware.auth import session_context


def create_app():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(
        __name__,
        template_folder=os.path.join(project_root, "templates"),
        static_folder=os.path.join(project_root, "static"),
    )
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "bari-lms-dev-key")
    app.config["PGHOST"] = os.environ.get("PGHOST", "127.0.0.1")
    app.config["PGPORT"] = int(os.environ.get("PGPORT", "5432"))
    app.config["PGDATABASE"] = os.environ.get("PGDATABASE", "bari_lms")
    app.config["PGUSER"] = os.environ.get("PGUSER", "postgres")
    app.config["PGPASSWORD"] = os.environ.get("PGPASSWORD", "")

    upload_folder = os.path.join(project_root, "static", "uploads", "guias")
    os.makedirs(upload_folder, exist_ok=True)
    app.config["UPLOAD_FOLDER_GUIAS"] = upload_folder

    app.extensions["db_pool"] = create_pool(app)
    app.teardown_appcontext(close_db)
    app.context_processor(session_context)

    register_auth_routes(app)
    register_dashboard_routes(app)
    register_admin_routes(app)
    register_instructor_routes(app)
    register_etapa_productiva_routes(app)

    with app.app_context():
        initialize_database()

    return app
