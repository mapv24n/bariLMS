import os

from flask import Flask

from bari_lms.controllers.admin_controller import register_routes as register_admin_routes
from bari_lms.controllers.auth_controller import register_routes as register_auth_routes
from bari_lms.controllers.dashboard_controller import register_routes as register_dashboard_routes
from bari_lms.controllers.instructor_controller import register_routes as register_instructor_routes
from bari_lms.models.repository import close_db, initialize_database
from bari_lms.services.auth import session_context


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "bari-lms-dev-key")
    app.config["PGHOST"] = os.environ.get("PGHOST", "127.0.0.1")
    app.config["PGPORT"] = int(os.environ.get("PGPORT", "5432"))
    app.config["PGDATABASE"] = os.environ.get("PGDATABASE", "bari_lms")
    app.config["PGUSER"] = os.environ.get("PGUSER", "postgres")
    app.config["PGPASSWORD"] = os.environ.get("PGPASSWORD", "")

    app.teardown_appcontext(close_db)
    app.context_processor(session_context)

    register_auth_routes(app)
    register_dashboard_routes(app)
    register_admin_routes(app)
    register_instructor_routes(app)

    with app.app_context():
        initialize_database()

    return app
