import copy
import os
import sqlite3
from functools import wraps

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "bari-lms-dev-key")
app.config["DATABASE"] = os.path.join(app.root_path, "bari_lms.db")

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

DASHBOARDS = {
    "administrador": {
        "role": "Administrador",
        "icon": "fa-user-shield",
        "area": "Direccionamiento institucional",
        "title": "Tablero del Administrador",
        "text": "Supervisa la operacion general de BARÍ LMS, define lineamientos y controla el acceso de los perfiles del LMS.",
        "footer": "BARÍ LMS SENA - Administrador",
        "menu_heading": "Administracion",
        "menu": [
            {"icon": "fa-users-cog", "label": "Usuarios y roles", "endpoint": "admin_users"},
            {"icon": "fa-chart-pie", "label": "Indicadores", "endpoint": "dashboard", "endpoint_kwargs": {"role_slug": "administrador"}},
        ],
        "metrics": [
            {"label": "Usuarios activos", "value": "0", "icon": "fa-users"},
            {"label": "Centros vinculados", "value": "14", "icon": "fa-building"},
            {"label": "Roles configurados", "value": "0", "icon": "fa-user-shield"},
            {"label": "Sesiones hoy", "value": "326", "icon": "fa-sign-in-alt"},
        ],
        "tasks_title": "Frentes prioritarios",
        "tasks": [
            {"title": "Gestion de usuarios", "text": "Aprobar nuevas cuentas y validar asignacion de perfiles."},
            {"title": "Configuracion LMS", "text": "Definir parametros base, regionales y politicas institucionales."},
            {"title": "Seguimiento", "text": "Consultar indicadores de uso, permanencia y actividad por centro."},
        ],
        "table_title": "Resumen operativo",
        "table_headers": ["Unidad", "Estado", "Observacion"],
        "table_rows": [
            ["Regional Distrito Capital", "98%", "Sin novedades"],
            ["Regional Antioquia", "94%", "Actualizar instructores"],
            ["Regional Valle", "91%", "Revision de permisos"],
        ],
    },
    "administrativo": {
        "role": "Administrativo",
        "icon": "fa-clipboard-check",
        "area": "Apoyo academico y operativo",
        "title": "Tablero Administrativo",
        "text": "Consolida fichas, programas, ambientes y apoyo documental para el despliegue de la formacion por proyectos.",
        "footer": "BARÍ LMS SENA - Administrativo",
        "menu_heading": "Operacion",
        "menu": [
            {"icon": "fa-folder-open", "label": "Fichas y programas", "endpoint": "dashboard", "endpoint_kwargs": {"role_slug": "administrativo"}},
            {"icon": "fa-school", "label": "Ambientes y sedes", "endpoint": "dashboard", "endpoint_kwargs": {"role_slug": "administrativo"}},
        ],
        "metrics": [
            {"label": "Fichas activas", "value": "86", "icon": "fa-id-badge"},
            {"label": "Programas", "value": "27", "icon": "fa-graduation-cap"},
            {"label": "Ambientes", "value": "49", "icon": "fa-door-open"},
            {"label": "Solicitudes", "value": "12", "icon": "fa-clipboard-list"},
        ],
        "tasks_title": "Pendientes",
        "tasks": [
            {"title": "Matricula", "text": "Consolidar aprendices por ficha y programa."},
            {"title": "Ambientes", "text": "Validar capacidad y disponibilidad por sede."},
            {"title": "Soporte documental", "text": "Publicar formatos y circulares internas."},
        ],
        "table_title": "Control academico",
        "table_headers": ["Ficha", "Programa", "Estado"],
        "table_rows": [
            ["ADSI 2675854", "Analisis y Desarrollo", "Completa"],
            ["SST 2675921", "Seguridad y Salud", "Pendiente soporte"],
            ["Cocina 2676018", "Tecnico en Cocina", "Actualizada"],
        ],
    },
    "instructor": {
        "role": "Instructor",
        "icon": "fa-chalkboard-teacher",
        "area": "Ejecucion formativa",
        "title": "Tablero del Instructor",
        "text": "Organiza resultados de aprendizaje, evidencias, proyectos y seguimiento del avance de cada ficha.",
        "footer": "BARÍ LMS SENA - Instructor",
        "menu_heading": "Formacion",
        "menu": [
            {"icon": "fa-book-reader", "label": "Planeacion", "endpoint": "dashboard", "endpoint_kwargs": {"role_slug": "instructor"}},
            {"icon": "fa-clipboard-check", "label": "Evaluacion", "endpoint": "dashboard", "endpoint_kwargs": {"role_slug": "instructor"}},
        ],
        "metrics": [
            {"label": "Fichas a cargo", "value": "6", "icon": "fa-layer-group"},
            {"label": "Proyectos activos", "value": "18", "icon": "fa-project-diagram"},
            {"label": "Evidencias por revisar", "value": "43", "icon": "fa-tasks"},
            {"label": "Alertas de asistencia", "value": "5", "icon": "fa-user-clock"},
        ],
        "tasks_title": "Acciones docentes",
        "tasks": [
            {"title": "Planeacion", "text": "Programar actividades alineadas al proyecto formativo."},
            {"title": "Seguimiento", "text": "Retroalimentar evidencias y avances semanales."},
            {"title": "Evaluacion", "text": "Registrar desempeno por resultado de aprendizaje."},
        ],
        "table_title": "Seguimiento de fichas",
        "table_headers": ["Ficha", "Actividad", "Estado"],
        "table_rows": [
            ["Ficha 2675854", "Sprint de prototipo", "15 entregas pendientes"],
            ["Ficha 2675860", "Sustentacion parcial", "Programada"],
            ["Ficha 2675902", "Bitacora de proyecto", "Al dia"],
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
            {"icon": "fa-project-diagram", "label": "Mi proyecto", "endpoint": "dashboard", "endpoint_kwargs": {"role_slug": "aprendiz"}},
            {"icon": "fa-file-alt", "label": "Evidencias", "endpoint": "dashboard", "endpoint_kwargs": {"role_slug": "aprendiz"}},
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
            {"title": "Comunicacion", "text": "Revisar mensajes de instructor y coordinacion."},
        ],
        "table_title": "Proximas entregas",
        "table_headers": ["Actividad", "Fecha", "Estado"],
        "table_rows": [
            ["Bitacora semanal", "14 de marzo de 2026", "Pendiente"],
            ["Prototipo funcional", "18 de marzo de 2026", "En progreso"],
            ["Autoevaluacion", "20 de marzo de 2026", "No iniciada"],
        ],
    },
}


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def initialize_database():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.commit()

    user_count = db.execute("SELECT COUNT(*) AS total FROM users").fetchone()["total"]
    if user_count == 0:
        for user in DEFAULT_USERS:
            db.execute(
                """
                INSERT INTO users (email, password_hash, role, name, active)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user["email"],
                    generate_password_hash(user["password"]),
                    user["role"],
                    user["name"],
                    user["active"],
                ),
            )
        db.commit()


with app.app_context():
    initialize_database()


def get_user_by_email(email):
    if not email:
        return None
    return get_db().execute(
        """
        SELECT id, email, role, name, active, created_at, password_hash
        FROM users
        WHERE lower(email) = lower(?)
        """,
        (email,),
    ).fetchone()


def get_user_by_id(user_id):
    return get_db().execute(
        """
        SELECT id, email, role, name, active, created_at
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()


def get_all_users():
    return get_db().execute(
        """
        SELECT id, email, role, name, active, created_at
        FROM users
        ORDER BY created_at DESC, id DESC
        """
    ).fetchall()


def get_admin_dashboard_data():
    db = get_db()
    total_active = db.execute("SELECT COUNT(*) AS total FROM users WHERE active = 1").fetchone()["total"]
    total_roles = db.execute("SELECT COUNT(DISTINCT role) AS total FROM users").fetchone()["total"]
    latest_users = db.execute(
        """
        SELECT name, role, email
        FROM users
        ORDER BY created_at DESC, id DESC
        LIMIT 3
        """
    ).fetchall()

    config = copy.deepcopy(DASHBOARDS["administrador"])
    config["metrics"][0]["value"] = str(total_active)
    config["metrics"][2]["value"] = str(total_roles)
    config["table_title"] = "Ultimos usuarios registrados"
    config["table_headers"] = ["Nombre", "Rol", "Correo"]
    config["table_rows"] = [[row["name"], row["role"], row["email"]] for row in latest_users] or [
        ["Sin registros", "-", "-"]
    ]
    return config


def current_user():
    email = session.get("user_email")
    if not email:
        return None

    user = get_user_by_email(email)
    if user is None or user["active"] != 1:
        session.clear()
        return None

    return {
        "id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "name": user["name"],
        "active": user["active"],
        "dashboard_slug": ROLE_TO_SLUG[user["role"]],
    }


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        user = current_user()
        if user is None:
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


def role_required(expected_role):
    def decorator(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            user = current_user()
            if user is None:
                return redirect(url_for("login"))
            if user["role"] != expected_role:
                return redirect(url_for("dashboard", role_slug=user["dashboard_slug"]))
            return view(**kwargs)

        return wrapped_view

    return decorator


@app.context_processor
def inject_session_user():
    return {
        "session_user": current_user(),
        "session_user_email": session.get("user_email", ""),
    }


@app.route("/")
def home():
    user = current_user()
    if user:
        return redirect(url_for("dashboard", role_slug=user["dashboard_slug"]))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "")
        user = get_user_by_email(email)

        if (
            user is None
            or user["active"] != 1
            or user["role"] != role
            or not check_password_hash(user["password_hash"], password)
        ):
            flash("Credenciales o perfil incorrectos. Usa uno de los accesos demo listados.", "danger")
            return render_template("login.html", demo_users=DEFAULT_USERS)

        session.clear()
        session["user_email"] = user["email"]
        return redirect(url_for("dashboard", role_slug=ROLE_TO_SLUG[user["role"]]))

    if current_user():
        return redirect(url_for("home"))

    return render_template("login.html", demo_users=DEFAULT_USERS)


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


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


@app.route("/admin/users")
@role_required("Administrador")
def admin_users():
    return render_template(
        "admin_users.html",
        user=current_user(),
        users=get_all_users(),
        roles=AVAILABLE_ROLES,
        form_data={},
        editing_user=None,
    )


@app.post("/admin/users/create")
@role_required("Administrador")
def admin_users_create():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    role = request.form.get("role", "").strip()
    password = request.form.get("password", "")
    active = 1 if request.form.get("active") == "on" else 0

    form_data = {"name": name, "email": email, "role": role, "active": active}

    if not name or not email or not role or not password:
        flash("Todos los campos son obligatorios para crear el usuario.", "danger")
        return render_template(
            "admin_users.html",
            user=current_user(),
            users=get_all_users(),
            roles=AVAILABLE_ROLES,
            form_data=form_data,
            editing_user=None,
        )

    if role not in AVAILABLE_ROLES:
        flash("El rol seleccionado no es valido.", "danger")
        return redirect(url_for("admin_users"))

    db = get_db()
    existing = get_user_by_email(email)
    if existing is not None:
        flash("Ya existe un usuario registrado con ese correo.", "danger")
        return render_template(
            "admin_users.html",
            user=current_user(),
            users=get_all_users(),
            roles=AVAILABLE_ROLES,
            form_data=form_data,
            editing_user=None,
        )

    db.execute(
        """
        INSERT INTO users (email, password_hash, role, name, active)
        VALUES (?, ?, ?, ?, ?)
        """,
        (email, generate_password_hash(password), role, name, active),
    )
    db.commit()
    flash("Usuario creado correctamente.", "success")
    return redirect(url_for("admin_users"))


@app.get("/admin/users/<int:user_id>/edit")
@role_required("Administrador")
def admin_users_edit(user_id):
    editing_user = get_user_by_id(user_id)
    if editing_user is None:
        flash("El usuario solicitado no existe.", "danger")
        return redirect(url_for("admin_users"))

    return render_template(
        "admin_users.html",
        user=current_user(),
        users=get_all_users(),
        roles=AVAILABLE_ROLES,
        form_data={
            "name": editing_user["name"],
            "email": editing_user["email"],
            "role": editing_user["role"],
            "active": editing_user["active"],
        },
        editing_user=editing_user,
    )


@app.post("/admin/users/<int:user_id>/update")
@role_required("Administrador")
def admin_users_update(user_id):
    editing_user = get_user_by_id(user_id)
    if editing_user is None:
        flash("El usuario solicitado no existe.", "danger")
        return redirect(url_for("admin_users"))

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    role = request.form.get("role", "").strip()
    password = request.form.get("password", "")
    active = 1 if request.form.get("active") == "on" else 0

    if not name or not email or not role:
        flash("Nombre, correo y rol son obligatorios.", "danger")
        return redirect(url_for("admin_users_edit", user_id=user_id))

    if role not in AVAILABLE_ROLES:
        flash("El rol seleccionado no es valido.", "danger")
        return redirect(url_for("admin_users_edit", user_id=user_id))

    existing = get_user_by_email(email)
    if existing is not None and existing["id"] != user_id:
        flash("Ya existe otro usuario con ese correo.", "danger")
        return redirect(url_for("admin_users_edit", user_id=user_id))

    if current_user()["id"] == user_id and active != 1:
        flash("No puedes desactivar tu propia cuenta mientras la estas usando.", "danger")
        return redirect(url_for("admin_users_edit", user_id=user_id))

    db = get_db()
    if password:
        db.execute(
            """
            UPDATE users
            SET name = ?, email = ?, role = ?, active = ?, password_hash = ?
            WHERE id = ?
            """,
            (name, email, role, active, generate_password_hash(password), user_id),
        )
    else:
        db.execute(
            """
            UPDATE users
            SET name = ?, email = ?, role = ?, active = ?
            WHERE id = ?
            """,
            (name, email, role, active, user_id),
        )
    db.commit()

    if current_user()["id"] == user_id:
        session["user_email"] = email

    flash("Usuario actualizado correctamente.", "success")
    return redirect(url_for("admin_users"))


@app.post("/admin/users/<int:user_id>/delete")
@role_required("Administrador")
def admin_users_delete(user_id):
    target_user = get_user_by_id(user_id)
    if target_user is None:
        flash("El usuario solicitado no existe.", "danger")
        return redirect(url_for("admin_users"))

    if current_user()["id"] == user_id:
        flash("No puedes eliminar tu propia cuenta.", "danger")
        return redirect(url_for("admin_users"))

    db = get_db()
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    flash("Usuario eliminado correctamente.", "success")
    return redirect(url_for("admin_users"))


if __name__ == "__main__":
    app.run(debug=True)
