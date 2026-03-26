"""Etapa Productiva — dispatcher central: redirige al sub-módulo del rol."""

from flask import redirect, render_template, url_for

from bari_lms.middleware.auth import current_user, login_required

# Roles con sub-módulo EP propio → endpoint de destino
_EP_ROUTES = {
    "instructor": "ep_instructor_fichas",
}

# Base template a usar en novedades para cada rol sin sub-módulo EP todavía
_ROLE_BASE = {
    "administrador": "admin/base.html",
    "administrativo": "admin/base.html",
    "aprendiz":       "aprendiz/base.html",
    "empresa":        "admin/base.html",
}


def register_routes(app):
    @app.route("/etapa-productiva")
    @login_required
    def ep_index():
        user = current_user()
        slug = user["dashboard_slug"]

        if slug in _EP_ROUTES:
            return redirect(url_for(_EP_ROUTES[slug]))

        base = _ROLE_BASE.get(slug, "admin/base.html")
        return render_template(
            "etapa_productiva/novedades/proximamente.html",
            user=user,
            base_template=base,
        )
