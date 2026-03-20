# BARÍ LMS — Sistema de Gestión de Formación SENA

> Plataforma web para la gestión de la formación por proyectos del Servicio Nacional de Aprendizaje (SENA), desarrollada como proyecto integrador del programa de Análisis y Desarrollo de Software.

---

## Índice

- [Tecnologías](#tecnologías)
- [Requisitos previos](#requisitos-previos)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Usuarios de prueba](#usuarios-de-prueba)
- [Roles y accesos](#roles-y-accesos)
- [Módulos implementados](#módulos-implementados)
- [Rutas disponibles](#rutas-disponibles)
- [Equipo de desarrollo](#equipo-de-desarrollo)

---

## Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11+ · Flask 3.x |
| Base de datos | PostgreSQL 17+ |
| Driver BD | `psycopg` 3.x (psycopg3) |
| Seguridad | `werkzeug.security` — hashing scrypt |
| Frontend | Bootstrap 4 (SB Admin 2) · Jinja2 |
| Íconos | Font Awesome 5 |
| Tipografía | Google Fonts — Nunito |

---

## Requisitos previos

- **Python 3.11** o superior
- **PostgreSQL 17** o superior corriendo localmente (pgAdmin, DBngin, Postgres.app, etc.)
- **pip**

---

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/SENA-2025/bariLMS.git
cd bariLMS
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo de ejemplo y edita tus credenciales de PostgreSQL:

```bash
cp .env.example .env
```

Abre `.env` y ajusta los valores:

```env
SECRET_KEY=cambia-esto-en-produccion

PGHOST=127.0.0.1
PGPORT=5432
PGDATABASE=bari_lms      # nombre de tu base de datos
PGUSER=postgres          # tu usuario de PostgreSQL
PGPASSWORD=              # tu contraseña
```

### 5. Crear la base de datos, el schema y los datos base

Crea la base de datos vacía:

```bash
createdb -U postgres bari_lms
```

Aplica el schema (tablas, índices, constraints):

```bash
psql -U postgres -d bari_lms -f database/bari_lms_postgresql.sql
```

Aplica los datos de catálogo (perfiles, tipos de documento, niveles, fases…):

```bash
psql -U postgres -d bari_lms -f database/seed.sql
```

### 6. Ejecutar la aplicación — primer inicio

Al arrancar sin usuarios administradores la app genera automáticamente
un **admin provisional** con correo y contraseña aleatorios, imprimiéndolos
una sola vez en la consola. Úsalos para el primer acceso y crea tu cuenta real
desde el panel de administración.

### 7. Ejecutar la aplicación

```bash
python run.py
```

Accede en el navegador: `http://127.0.0.1:5000`

---

## Estructura del proyecto

```
bariLMS/
├── run.py                          ← Punto de entrada de la aplicación
├── requirements.txt                ← Dependencias Python
├── .env.example                    ← Plantilla de variables de entorno
│
└── internal/
    ├── bari_lms/                   ← Paquete principal (MVC)
    │   ├── __init__.py             ← Factory create_app()
    │   ├── config.py               ← Roles, dashboards y usuarios por defecto
    │   ├── controllers/            ← Rutas por módulo (auth, admin, instructor, dashboard)
    │   ├── models/
    │   │   ├── repository.py       ← Conexión PostgreSQL + inicialización de schema
    │   │   └── instructor.py       ← Modelo instructor
    │   └── services/               ← Lógica de negocio (auth, instructor)
    │
    ├── templates/                  ← Plantillas Jinja2
    │   ├── login.html
    │   ├── dashboard.html
    │   ├── 404.html
    │   ├── admin_*.html
    │   ├── aprendiz/
    │   ├── instructor/
    │   └── components/
    │
    ├── static/                     ← Assets (CSS, JS, imágenes)
    │   ├── css/
    │   ├── js/
    │   ├── img/
    │   └── uploads/                ← Archivos subidos por usuarios (ignorado en git)
    │
    └── database/
        ├── bari_lms_postgresql.sql ← Schema completo de referencia
        ├── setup_aprendiz.sql      ← Tablas específicas de la vista aprendiz
        ├── seed_pg.py              ← Seed principal (PostgreSQL)
        └── seed_aprendices.py      ← Seed de aprendices de prueba (PostgreSQL)
```

> **Nota:** Las tablas **no** se crean automáticamente. Es necesario ejecutar el schema antes del primer inicio de la app.

---

## Admin provisional (primer inicio)

Al arrancar sin ningún usuario con perfil **Administrador**, la app genera
automáticamente una cuenta provisional con credenciales aleatorias:

```
[bariLMS] ⚠  No se encontró ningún administrador.
[bariLMS]    Correo     : admin_x7k2p9@senalearn.edu.co
[bariLMS]    Contraseña : Xq8#mL3vR2
[bariLMS]    Úsalas para el primer acceso y crea tu cuenta real de inmediato.
```

> Esta cuenta es de un solo uso. Crea un administrador real desde el panel
> y desactiva la provisional.

---

## Roles y accesos

| Perfil | Ruta dashboard | Descripción |
|---|---|---|
| **Administrador** | `/dashboard/administrador` | Usuarios, estructura institucional y académica |
| **Administrativo** | `/dashboard/administrativo` | Fichas, programas, ambientes y soporte documental |
| **Instructor** | `/dashboard/instructor` | Fichas, fases, actividades y calificación de aprendices |
| **Aprendiz** | `/dashboard/aprendiz` | Dashboard, fichas, fases, evidencias y calificaciones |
| **Empresa** | `/dashboard/empresa` | Seguimiento de aprendices en etapa productiva |

> Si un usuario tiene **un único perfil** se redirige directamente a su dashboard.
> Si tiene **varios perfiles** la app muestra un selector para elegir.

---

## Módulos implementados

### Vista Aprendiz

| Módulo | Ruta | Descripción |
|---|---|---|
| Dashboard | `/dashboard/aprendiz` | Panel con ficha, programa y accesos rápidos |
| Mis Fichas | `/aprendiz/fichas` | Lista de fichas con búsqueda en tiempo real |
| Detalle de Ficha | `/aprendiz/ficha/<id>` | Fases, actividades y barra de progreso |
| Entrega de Evidencias | `POST /aprendiz/entregar-evidencia` | Envío de URL de evidencia por actividad |
| Fases de Formación | `/aprendiz/fases` | Estructura de fases: Análisis, Planeación, Ejecución |
| Calificaciones | `/aprendiz/calificaciones` | Historial de notas con resumen estadístico |
| Cambiar Contraseña | `/aprendiz/cambiar-contrasena` | Actualización segura de credenciales |
| Notificaciones | Campana en topbar | Alertas sin leer con marcado por AJAX |

### Vista Instructor

| Módulo | Ruta | Descripción |
|---|---|---|
| Fichas | `/instructor/fichas` | Fichas asignadas al instructor |
| Fases y Actividades | `/instructor/ficha/<id>/fases` | Árbol dinámico de fases y actividades |
| Calificación | Modal en fases | Calificación 0–100, aprueba con ≥ 75 |
| Cambiar Contraseña | `/instructor/change-password` | Actualización de credenciales |

### Vista Administrador

| Módulo | Descripción |
|---|---|
| Gestión de usuarios | CRUD completo de usuarios por rol |
| Estructura institucional | Regionales, centros, coordinaciones, sedes, ambientes |
| Estructura académica | Programas, fichas, proyectos, fases y actividades |

---

## Rutas disponibles

### Autenticación

| Método | Ruta | Descripción |
|---|---|---|
| GET/POST | `/login` | Inicio de sesión |
| GET/POST | `/logout` | Cierre de sesión |

### Aprendiz

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/dashboard/aprendiz` | Panel principal |
| GET | `/aprendiz/fichas` | Lista de fichas |
| GET | `/aprendiz/ficha/<id>` | Detalle de ficha |
| GET | `/aprendiz/fases` | Fases de formación |
| GET | `/aprendiz/calificaciones` | Historial de calificaciones |
| GET/POST | `/aprendiz/cambiar-contrasena` | Cambio de contraseña |
| POST | `/aprendiz/entregar-evidencia` | Entregar evidencia (URL) |
| POST | `/aprendiz/notificaciones/marcar-leida/<id>` | Marcar notificación leída |

### Instructor

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/dashboard/instructor` | Panel principal |
| GET | `/instructor/fichas` | Fichas asignadas |
| GET | `/instructor/ficha/<id>/fases` | Fases y actividades |
| GET/POST | `/instructor/change-password` | Cambio de contraseña |

---

## Equipo de desarrollo

| Nombre | Rol en el proyecto | Rama |
|---|---|---|
| Santiago | Vista Aprendiz | `Santiago-Vista_Aprendiz` |
| Ana María | Vista Instructor | `Anamaria-VistaInstructor` |
