import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'sena_key_2026'

# --- CONFIGURACIÓN DE BASE DE DATOS ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'senalearn',
    'port': 5435
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error crítico de conexión: {e}")
        return None

# --- FUNCIONES DE CONSULTA ---

def get_user_by_email(email):
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM usuarios WHERE LOWER(email) = LOWER(%s)", (email.strip(),))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def get_user_by_id(user_id):
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def get_aprendiz_full_data(user_id):
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT u.nombre, f.numero AS ficha_numero, p.nombre AS programa_nombre
            FROM usuarios u
            LEFT JOIN aprendices a ON u.id = a.id
            LEFT JOIN fichas f ON a.ficha_id = f.id
            LEFT JOIN programas_formacion p ON f.programa_id = p.id
            WHERE u.id = %s
        """, (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def get_notificaciones(user_id):
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT * FROM notificaciones
            WHERE usuario_id = %s AND leida = 0
            ORDER BY creado_en DESC
        """, (user_id,))
        return cursor.fetchall()
    except Error:
        return []
    finally:
        cursor.close()
        conn.close()

# --- RUTAS DE AUTENTICACIÓN ---

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        rol_seleccionado = request.form.get("role", "")

        user = get_user_by_email(email)

        if user:
            if check_password_hash(user["password_hash"], password):
                if user["rol"].lower() == rol_seleccionado.lower():
                    session.clear()
                    session["user_id"] = user["id"]
                    session["nombre"] = user["nombre"]
                    session["rol"] = user["rol"]
                    role_path = "aprendiz" if user["rol"].lower() == "aprendiz" else "admin"
                    return redirect(url_for("dashboard", role_slug=role_path))
                else:
                    flash("El perfil seleccionado no coincide con tu cuenta.", "warning")
            else:
                flash("Correo o contraseña incorrectos.", "danger")
        else:
            flash("El correo no está registrado.", "danger")

    return render_template("login.html")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- DASHBOARD ---

@app.route("/dashboard/<role_slug>")
def dashboard(role_slug):
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_info = get_aprendiz_full_data(session["user_id"])
    if role_slug == "aprendiz":
        notificaciones = get_notificaciones(session["user_id"])
        return render_template("aprendiz/dashboard.html", user_info=user_info, notificaciones=notificaciones)
    return render_template("dashboard.html", user_info=user_info)

# --- RUTAS DEL APRENDIZ ---

@app.route("/aprendiz/fichas")
def aprendiz_fichas():
    if "user_id" not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    fichas = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT f.id, f.numero, p.nombre AS programa_nombre
            FROM aprendices a
            JOIN fichas f ON a.ficha_id = f.id
            JOIN programas_formacion p ON f.programa_id = p.id
            WHERE a.id = %s
        """, (session["user_id"],))
        fichas = cursor.fetchall()
        cursor.close()
        conn.close()
    notificaciones = get_notificaciones(session["user_id"])
    return render_template("aprendiz/fichas.html", fichas=fichas, notificaciones=notificaciones)

@app.route("/aprendiz/ficha/<int:ficha_id>")
def aprendiz_ficha_detalle(ficha_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection()
    if not conn:
        flash("Error de conexión.", "danger")
        return redirect(url_for("aprendiz_fichas"))
    cursor = conn.cursor(dictionary=True)

    # Verificar que la ficha pertenece al aprendiz
    cursor.execute("""
        SELECT f.id, f.numero, p.nombre AS programa_nombre,
               n.nombre AS nivel_nombre, mo.nombre AS modalidad_nombre
        FROM aprendices a
        JOIN fichas f ON a.ficha_id = f.id
        JOIN programas_formacion p ON f.programa_id = p.id
        LEFT JOIN niveles n ON p.nivel_id = n.id
        LEFT JOIN modalidades mo ON p.modalidad_id = mo.id
        WHERE a.id = %s AND f.id = %s
    """, (session["user_id"], ficha_id))
    ficha = cursor.fetchone()

    if not ficha:
        cursor.close()
        conn.close()
        flash("No tienes acceso a esa ficha.", "warning")
        return redirect(url_for("aprendiz_fichas"))

    # Fases con sus actividades de proyecto
    fases_dict = {}
    try:
        cursor.execute("""
            SELECT fa.id AS fase_id, fa.nombre AS fase_nombre, fa.orden,
                   ap.id AS ap_id, ap.nombre AS ap_nombre, ap.codigo AS ap_codigo
            FROM fases fa
            LEFT JOIN actividades_proyecto ap ON ap.fase_id = fa.id AND ap.ficha_id = %s
            ORDER BY fa.orden, ap.id
        """, (ficha_id,))
        for row in cursor.fetchall():
            fid = row["fase_id"]
            if fid not in fases_dict:
                fases_dict[fid] = {"fase_nombre": row["fase_nombre"], "orden": row["orden"], "actividades": []}
            if row["ap_id"]:
                fases_dict[fid]["actividades"].append({
                    "id": row["ap_id"], "nombre": row["ap_nombre"], "codigo": row["ap_codigo"]
                })
    except Error:
        pass

    # Calcular progreso
    total, aprobadas, porcentaje = 0, 0, 0
    try:
        cursor.execute("""
            SELECT COUNT(aa.id) AS total,
                   SUM(CASE WHEN ee.aprueba = 1 THEN 1 ELSE 0 END) AS aprobadas
            FROM actividades_proyecto ap
            JOIN actividades_aprendizaje aa ON aa.actividad_proyecto_id = ap.id
            LEFT JOIN entrega_evidencia ee ON ee.actividad_aprendizaje_id = aa.id
                       AND ee.aprendiz_id = %s
            WHERE ap.ficha_id = %s
        """, (session["user_id"], ficha_id))
        progreso = cursor.fetchone()
        if progreso:
            total = progreso["total"] or 0
            aprobadas = int(progreso["aprobadas"] or 0)
            porcentaje = int((aprobadas / total) * 100) if total > 0 else 0
    except Error:
        pass

    # Entregas del aprendiz para esta ficha (para mostrar estado en el detalle)
    entregas = {}
    try:
        cursor.execute("""
            SELECT ee.actividad_aprendizaje_id, ee.url_evidencia,
                   ee.calificacion, ee.aprueba, ee.fecha_entrega
            FROM entrega_evidencia ee
            JOIN actividades_aprendizaje aa ON ee.actividad_aprendizaje_id = aa.id
            JOIN actividades_proyecto ap ON aa.actividad_proyecto_id = ap.id
            WHERE ee.aprendiz_id = %s AND ap.ficha_id = %s
        """, (session["user_id"], ficha_id))
        for e in cursor.fetchall():
            entregas[e["actividad_aprendizaje_id"]] = e
    except Error:
        pass

    cursor.close()
    conn.close()

    notificaciones = get_notificaciones(session["user_id"])
    return render_template("aprendiz/ficha_detalle.html",
                           ficha=ficha,
                           fases=list(fases_dict.values()),
                           total=total,
                           aprobadas=aprobadas,
                           porcentaje=porcentaje,
                           entregas=entregas,
                           notificaciones=notificaciones)

@app.route("/aprendiz/fases")
def aprendiz_fases():
    if "user_id" not in session:
        return redirect(url_for('login'))
    ficha = get_aprendiz_full_data(session["user_id"])
    notificaciones = get_notificaciones(session["user_id"])
    return render_template("aprendiz/fases.html", ficha=ficha, notificaciones=notificaciones)

@app.route("/aprendiz/calificaciones")
def aprendiz_calificaciones():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection()
    calificaciones = []
    resumen = {"total": 0, "aprobadas": 0, "pendientes": 0, "promedio": 0}
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT fa.nombre AS fase_nombre,
                       ap.nombre AS actividad_proyecto_nombre,
                       aa.nombre AS actividad_aprendizaje_nombre,
                       ee.url_evidencia, ee.fecha_entrega,
                       ee.calificacion, ee.aprueba,
                       ee.retroalimentacion, ee.calificado_en,
                       f.numero AS ficha_numero
                FROM entrega_evidencia ee
                JOIN actividades_aprendizaje aa ON ee.actividad_aprendizaje_id = aa.id
                JOIN actividades_proyecto ap ON aa.actividad_proyecto_id = ap.id
                JOIN fases fa ON ap.fase_id = fa.id
                JOIN fichas f ON ap.ficha_id = f.id
                WHERE ee.aprendiz_id = %s
                ORDER BY fa.orden, ap.id, aa.id
            """, (session["user_id"],))
            calificaciones = cursor.fetchall()

            cursor.execute("""
                SELECT COUNT(*) AS total,
                       SUM(CASE WHEN calificacion IS NOT NULL THEN 1 ELSE 0 END) AS calificadas,
                       SUM(CASE WHEN aprueba = 1 THEN 1 ELSE 0 END) AS aprobadas,
                       AVG(CASE WHEN calificacion IS NOT NULL THEN calificacion END) AS promedio
                FROM entrega_evidencia WHERE aprendiz_id = %s
            """, (session["user_id"],))
            stats = cursor.fetchone()
            if stats:
                resumen["total"] = stats["total"] or 0
                resumen["aprobadas"] = int(stats["aprobadas"] or 0)
                resumen["pendientes"] = resumen["total"] - int(stats["calificadas"] or 0)
                resumen["promedio"] = round(float(stats["promedio"] or 0), 1)
        except Error:
            pass
        cursor.close()
        conn.close()
    notificaciones = get_notificaciones(session["user_id"])
    return render_template("aprendiz/calificaciones.html",
                           calificaciones=calificaciones,
                           resumen=resumen,
                           notificaciones=notificaciones)

@app.route("/aprendiz/cambiar-contrasena", methods=["GET", "POST"])
def aprendiz_cambiar_contrasena():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        actual = request.form.get("current_password", "")
        nueva = request.form.get("new_password", "")
        confirmar = request.form.get("confirm_password", "")

        if len(nueva) < 8:
            flash("La nueva contraseña debe tener al menos 8 caracteres.", "warning")
            return redirect(url_for("aprendiz_cambiar_contrasena"))
        if nueva != confirmar:
            flash("Las contraseñas nuevas no coinciden.", "danger")
            return redirect(url_for("aprendiz_cambiar_contrasena"))

        user = get_user_by_id(session["user_id"])
        if not user or not check_password_hash(user["password_hash"], actual):
            flash("La contraseña actual es incorrecta.", "danger")
            return redirect(url_for("aprendiz_cambiar_contrasena"))

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET password_hash = %s WHERE id = %s",
                           (generate_password_hash(nueva), session["user_id"]))
            conn.commit()
            cursor.close()
            conn.close()
        flash("Contraseña actualizada correctamente.", "success")
        return redirect(url_for("aprendiz_cambiar_contrasena"))

    notificaciones = get_notificaciones(session["user_id"])
    return render_template("aprendiz/cambiar_contrasena.html", notificaciones=notificaciones)

@app.route("/aprendiz/entregar-evidencia", methods=["POST"])
def aprendiz_entregar_evidencia():
    if "user_id" not in session:
        return redirect(url_for("login"))
    actividad_id = request.form.get("actividad_aprendizaje_id", type=int)
    url_evidencia = request.form.get("url_evidencia", "").strip()
    ficha_id = request.form.get("ficha_id", type=int)

    if not actividad_id or not url_evidencia:
        flash("Debes ingresar la URL de tu evidencia.", "warning")
        return redirect(url_for("aprendiz_ficha_detalle", ficha_id=ficha_id))
    if not (url_evidencia.startswith("http://") or url_evidencia.startswith("https://")):
        flash("La URL debe comenzar con http:// o https://", "warning")
        return redirect(url_for("aprendiz_ficha_detalle", ficha_id=ficha_id))

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO entrega_evidencia (aprendiz_id, actividad_aprendizaje_id, url_evidencia, fecha_entrega)
            VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE url_evidencia = VALUES(url_evidencia), fecha_entrega = NOW()
        """, (session["user_id"], actividad_id, url_evidencia))
        conn.commit()
        cursor.close()
        conn.close()
    flash("Evidencia entregada correctamente.", "success")
    return redirect(url_for("aprendiz_ficha_detalle", ficha_id=ficha_id))

# --- NOTIFICACIONES (API JSON) ---

@app.route("/aprendiz/notificaciones/marcar-leida/<int:notif_id>", methods=["POST"])
def aprendiz_notificacion_leida(notif_id):
    if "user_id" not in session:
        return jsonify({"error": "no auth"}), 401
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE notificaciones SET leida = 1 WHERE id = %s AND usuario_id = %s",
                       (notif_id, session["user_id"]))
        conn.commit()
        cursor.close()
        conn.close()
    return jsonify({"ok": True})

# --- ERROR HANDLERS ---

@app.errorhandler(404)
def page_not_found(_e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(_e):
    return render_template("404.html"), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
