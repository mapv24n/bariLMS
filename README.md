# BARÍ LMS — Sistema de Gestión de Formación SENA

> Plataforma web para la gestión de la formación por proyectos del Servicio Nacional de Aprendizaje (SENA), desarrollada como proyecto integrador del programa de Análisis y Desarrollo de Software.

---

## Índice

- [Tecnologías](#tecnologías)
- [Requisitos previos](#requisitos-previos)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Estructura del proyecto](#estructura-del-proyecto)
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
| Driver BD | `psycopg` 3.x (psycopg3) + `psycopg-pool` |
| Seguridad | `argon2-cffi` — hashing Argon2 · `PyJWT` |
| Frontend | Bootstrap 4 (SB Admin 2) · Jinja2 |
| Íconos | Font Awesome 5 |
| Tipografía | Google Fonts — Nunito |
| Despliegue | `gunicorn` |

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
psql -U postgres -d bari_lms -f database/bari_EtapaProductiva_postgresql.sql
```

> El segundo archivo depende del primero; ejecútalos en ese orden.

Aplica los datos de catálogo (perfiles, tipos de documento, niveles, fases…):

```bash
python database/seed.py
```

### 6. Cargar datos de prueba (opcional)

Para desarrollo y QA existe un conjunto de seeds que crean instructores, aprendices, fichas
y empresas EP listos para usar. Ver [`database/seeds/README.md`](database/seeds/README.md).

```bash
python database/seeds/run_all.py
```

### 7. Primer inicio — admin provisional

Al arrancar sin usuarios administradores la app genera automáticamente
un **admin provisional** con correo y contraseña aleatorios, imprimiéndolos
una sola vez en la consola. Úsalos para el primer acceso y crea tu cuenta real
desde el panel de administración.

```
[bariLMS] ⚠  No se encontró ningún administrador.
[bariLMS]    Correo     : admin_x7k2p9@senalearn.edu.co
[bariLMS]    Contraseña : Xq8#mL3vR2
[bariLMS]    Úsalas para el primer acceso y crea tu cuenta real de inmediato.
```

> Esta cuenta es de un solo uso. Crea un administrador real desde el panel y desactívala.

### 8. Ejecutar la aplicación

```bash
python run.py
```

Accede en el navegador: `http://127.0.0.1:5000`

---

## Estructura del proyecto

```
bariLMS/
├── run.py                              ← Punto de entrada
├── requirements.txt                    ← Dependencias Python
├── .env.example                        ← Plantilla de variables de entorno
│
└── internal/
    ├── bari_lms/                       ← Paquete principal
    │   ├── __init__.py                 ← Factory create_app()
    │   ├── config.py                   ← Roles, slugs y configuración de dashboards
    │   │
    │   ├── db/                         ← Pool de conexiones PostgreSQL
    │   │   ├── __init__.py             ← get_db(), close_db(), create_pool()
    │   │   └── bootstrap.py            ← Inicialización de la BD al arranque
    │   │
    │   ├── controllers/                ← Rutas organizadas por zona
    │   │   ├── auth.py                 ← Login / logout
    │   │   ├── dashboard.py            ← Dashboard por rol
    │   │   ├── admin/                  ← Módulos del administrador
    │   │   │   ├── usuarios.py         ← CRUD de usuarios
    │   │   │   ├── personas.py         ← Instructores, aprendices, administrativos
    │   │   │   ├── estructura.py       ← Regionales, centros, coordinaciones, etc.
    │   │   │   └── academico.py        ← Programas, fichas, proyectos, fases
    │   │   └── instructor/             ← Módulos del instructor
    │   │       ├── fichas.py           ← Fichas asignadas y vista de fases
    │   │       ├── actividades.py      ← API REST de actividades, secciones, etc.
    │   │       └── perfil.py           ← Cambio de contraseña
    │   │
    │   ├── middleware/
    │   │   └── auth.py                 ← current_user(), role_required()
    │   │
    │   ├── repositories/               ← Capa de acceso a datos
    │   │   ├── _config.py              ← ENTITY_CONFIG y configuración de entidades
    │   │   ├── academico.py            ← Contexto y consultas académicas
    │   │   ├── entidad.py              ← CRUD genérico de entidades
    │   │   ├── estructura.py           ← Contexto de estructura institucional
    │   │   ├── personas.py             ← Vinculación persona ↔ usuario
    │   │   └── usuario.py              ← Consultas de usuario
    │   │
    │   ├── models/
    │   │   ├── repository.py           ← Modelo de conexión (legacy)
    │   │   └── instructor.py           ← Modelo instructor (legacy)
    │   │
    │   └── services/
    │       └── security.py             ← hash_password() / verify_password() — Argon2
    │
    ├── templates/                      ← Plantillas Jinja2
    │   ├── login.html
    │   ├── dashboard.html
    │   ├── 404.html
    │   ├── admin/                      ← base.html + users, people, structure, academic
    │   ├── instructor/                 ← base.html + fichas, fases, change_password
    │   ├── aprendiz/                   ← Plantillas (vistas en desarrollo)
    │   └── components/                 ← Fragmentos reutilizables (flash_messages, etc.)
    │
    ├── static/
    │   ├── css/
    │   ├── js/
    │   ├── img/
    │   ├── vendor/                     ← Bootstrap, DataTables, SortableJS, etc.
    │   └── uploads/                    ← Archivos subidos (ignorado en git)
    │
    └── database/
        ├── bari_lms_postgresql.sql     ← Schema completo (tablas, índices, constraints)
        ├── seed.py                     ← Datos de catálogo con UUIDs v7 (perfiles, tipos, fases…)
        └── setup_aprendiz.sql          ← Tablas adicionales de la vista aprendiz
```

> **Nota:** Las tablas **no** se crean automáticamente. Es necesario ejecutar el schema antes del primer inicio.

---

## Roles y accesos

| Perfil | Slug | Estado |
|---|---|---|
| **Administrador** | `administrador` | Implementado |
| **Instructor** | `instructor` | Implementado |
| **Aprendiz** | `aprendiz` | Dashboard placeholder — vistas en desarrollo |
| **Administrativo** | `administrativo` | Dashboard placeholder — vistas en desarrollo |
| **Empresa** | `empresa` | Dashboard placeholder — vistas en desarrollo |

> Si un usuario tiene **un único perfil** se redirige directamente a su dashboard.
> Si tiene **varios perfiles** la app muestra un selector para elegir.

---

## Módulos implementados

### Vista Administrador

| Módulo | Ruta | Descripción |
|---|---|---|
| Usuarios y roles | `/admin/users` | CRUD completo de usuarios con asignación de rol |
| Gestionar personas | `/admin/people` | Instructores, aprendices y personal administrativo + importación CSV |
| Estructura institucional | `/admin/structure` | Regionales, centros, coordinaciones, sedes y ambientes |
| Gestión académica | `/admin/academic` | Redes, áreas, programas, fichas, proyectos, fases y actividades |

### Vista Instructor

| Módulo | Ruta | Descripción |
|---|---|---|
| Mis Fichas | `/instructor/fichas` | Fichas asignadas al instructor |
| Fases y Actividades | `/instructor/ficha/<id>/fases` | Árbol dinámico de fases, actividades y secciones |
| Calificación | API en fases | Calificación 0–100, aprueba con ≥ 75 |
| Asistencia | API en fases | Registro de asistencia por ficha |
| Cambiar Contraseña | `/instructor/password` | Actualización de credenciales |

---

## Rutas disponibles

### Autenticación

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Redirige a `/login` |
| GET / POST | `/login` | Inicio de sesión |
| POST | `/logout` | Cierre de sesión |
| GET | `/dashboard/<role_slug>` | Dashboard por rol |

### Administrador — Usuarios

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/admin/users` | Listar usuarios |
| POST | `/admin/users/create` | Crear usuario |
| GET | `/admin/users/<id>/edit` | Cargar datos para edición |
| POST | `/admin/users/<id>/update` | Actualizar usuario |
| POST | `/admin/users/<id>/delete` | Eliminar usuario |

### Administrador — Personas

`<entity>` puede ser: `instructor`, `aprendiz`, `administrativo_persona`

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/admin/people` | Vista de gestión de personas |
| POST | `/admin/people/<entity>/create` | Crear persona + usuario vinculado |
| POST | `/admin/people/<entity>/import` | Importación masiva CSV |
| GET | `/admin/people/<entity>/<id>/edit` | Cargar persona para edición |
| POST | `/admin/people/<entity>/<id>/update` | Actualizar persona |
| POST | `/admin/people/<entity>/<id>/delete` | Eliminar persona y usuario vinculado |

### Administrador — Estructura institucional

`<entity>` puede ser: `regional`, `centro`, `coordinacion`, `sede`, `ambiente`

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/admin/structure` | Vista jerárquica de estructura |
| POST | `/admin/structure/<entity>/create` | Crear entidad |
| GET | `/admin/structure/<entity>/<id>/edit` | Cargar entidad para edición |
| POST | `/admin/structure/<entity>/<id>/update` | Actualizar entidad |
| POST | `/admin/structure/<entity>/<id>/delete` | Eliminar entidad |

### Administrador — Gestión académica

`<entity>` puede ser: `nivel`, `red`, `area`, `programa`, `ficha`, `proyecto_formativo`, `fase_proyecto`, `actividad_proyecto`, `actividad_aprendizaje`

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/admin/academic` | Vista jerárquica académica |
| POST | `/admin/academic/<entity>/create` | Crear entidad |
| GET | `/admin/academic/<entity>/<id>/edit` | Cargar entidad para edición |
| POST | `/admin/academic/<entity>/<id>/update` | Actualizar entidad |
| POST | `/admin/academic/<entity>/<id>/delete` | Eliminar entidad |

### Instructor — Vistas

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/instructor/fichas` | Fichas asignadas |
| GET | `/instructor/ficha/<id>/fases` | Árbol de fases y actividades |
| GET / POST | `/instructor/password` | Cambio de contraseña |

### Instructor — API REST

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/instructor/ficha/<id>/tree` | Árbol completo de fases/actividades de una ficha |
| POST | `/api/instructor/ficha/<id>/fase/nueva` | Crear fase en una ficha |
| POST | `/api/instructor/fase/<id>/actividad/nueva` | Crear actividad de proyecto en una fase |
| POST | `/api/instructor/actividad-proyecto/<id>/aprendizaje/nueva` | Crear actividad de aprendizaje |
| GET | `/api/instructor/actividad-proyecto/<id>/actividades-aprendizaje` | Listar actividades de aprendizaje |
| GET | `/api/instructor/actividad-proyecto/<id>/evidencias-matriz` | Matriz de evidencias |
| GET | `/api/instructor/actividad-proyecto/<id>/guias` | Listar guías de actividad de proyecto |
| POST | `/api/instructor/actividad-proyecto/<id>/guias/nueva` | Crear guía de actividad de proyecto |
| PATCH | `/api/instructor/actividad-proyecto/<id>/guias/orden` | Reordenar guías |
| PATCH | `/api/instructor/actividad-proyecto/<id>/aprendizaje/orden` | Reordenar actividades de aprendizaje |
| PATCH | `/api/instructor/actividad-aprendizaje/<id>/editar` | Editar actividad de aprendizaje |
| PATCH | `/api/instructor/actividad-aprendizaje/<id>/fecha-fin` | Actualizar fecha de cierre |
| PATCH | `/api/instructor/actividad-aprendizaje/<id>/secciones/orden` | Reordenar secciones |
| POST | `/api/instructor/actividad-aprendizaje/<id>/seccion/nueva` | Crear sección |
| POST | `/api/instructor/actividad/<id>/guia` | Guardar guía de actividad de aprendizaje |
| POST | `/api/instructor/actividad/<id>/evidencia` | Activar evidencia para una actividad |
| GET | `/api/instructor/actividad/<id>/aprendices` | Aprendices y entregas de una actividad |
| PATCH | `/api/instructor/guia-actividad-proyecto/<id>/editar` | Editar guía de actividad de proyecto |
| DELETE | `/api/instructor/guia-actividad-proyecto/<id>` | Eliminar guía |
| PATCH | `/api/instructor/seccion/<id>/editar` | Editar sección |
| DELETE | `/api/instructor/seccion/<id>` | Eliminar sección |
| PATCH | `/api/instructor/seccion/<id>/sub-secciones/orden` | Reordenar sub-secciones |
| POST | `/api/instructor/seccion/<id>/sub-seccion/nueva` | Crear sub-sección |
| PATCH | `/api/instructor/sub-seccion/<id>/editar` | Editar sub-sección |
| DELETE | `/api/instructor/sub-seccion/<id>` | Eliminar sub-sección |
| POST | `/api/instructor/entrega/<id>/calificar` | Calificar entrega de evidencia |
| GET | `/api/instructor/ficha/<id>/asistencia` | Obtener asistencia de una ficha |
| POST | `/api/instructor/ficha/<id>/asistencia` | Guardar registro de asistencia |

---

## Equipo de desarrollo

| Nombre | Rol en el proyecto | Rama |
|---|---|---|
| Santiago | Vista Aprendiz | `Santiago-Vista_Aprendiz` |
| Ana María | Vista Instructor | `Anamaria-VistaInstructor` |
