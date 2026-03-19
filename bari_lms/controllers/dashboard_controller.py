from flask import redirect, render_template, url_for

from bari_lms.config import DASHBOARDS
from bari_lms.models.repository import get_admin_dashboard_data
from bari_lms.services.auth import current_user, login_required


def register_routes(app):
    @app.route("/dashboard/<role_slug>")
    @login_required
    def dashboard(role_slug):
        user = current_user()
        config = DASHBOARDS.get(role_slug)

        if config is None:
            return redirect(url_for("home"))

        if user["dashboard_slug"] != role_slug:
            return redirect(url_for("dashboard", role_slug=user["dashboard_slug"]))

        if role_slug == "administrador":
            config = get_admin_dashboard_data()

        return render_template("dashboard.html", dashboard=config, user=user)
