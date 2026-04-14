# bariLMS — Claude Code Context

## Project Overview
Flask-based LMS for SENA (Colombian vocational training institution).
Manages the academic and productive-stage (Etapa Productiva) lifecycle of apprentices.

**Stack:** Python 3.14 · Flask · PostgreSQL · psycopg3 · psycopg-pool · Jinja2 · Bootstrap 4 (SB Admin 2 theme)

**Working branch:** `Andrew96RR-cambios-2` (base: `develop`)

---

## Key Architecture

### Database
- Schema in `database/bari_lms_postgresql.sql` (source of truth for table definitions)
- Migrations managed with **dbmate** → `database/migrations/`
- Run migrations: `dbmate --migrations-dir database/migrations up`
- Inspect DB: `python database/query.py "SELECT ..."`  ← always use specific columns + LIMIT
- Seeds: `python database/seeds/extraSeeds/run_all.py` (idempotent when constraints are correct)

### DB Connection
- `internal/bari_lms/db/__init__.py` wraps psycopg3 with a `PostgresConnection` class
- Placeholder style: `?` — the wrapper's `_normalize_query` converts `?` → `%s` for psycopg3
- **Every write must call `db.commit()` explicitly** — there is no auto-commit middleware
- UUIDs: use `gen_random_uuid()` in SQL for inserts; `uuid.uuid7()` in Python seed scripts

### Module Structure
```
internal/
  bari_lms/
    __init__.py                  # App factory
    db/__init__.py               # Connection pool + PostgresConnection wrapper
    controllers/
      etapa_productiva/
        instructores.py          # EP instructor routes (fichas, contratos)
        proceso_ep.py            # EP process management routes
    services/
      instructor_ep_service.py   # EP queries (aprendices, empresas, contratos)
      proceso_ep_service.py      # EP process queries (momentos 1/2/3)
    rutas/
      plantillas_ep_instructor.py  # Template path constants
    middleware/auth.py           # @role_required, current_user()
  templates/
    etapa_productiva/
      ficha_detalle.html         # Tabs: Aprendices / Empresas
      aprendices/aprendices_tab.html
      aprendiz/contrato/
        contrato_crear.html      # New contract form
        contrato_editar.html     # Edit contract form
      aprendiz/gestionar/        # EP process management (momentos)
database/
  migrations/                    # dbmate migration files
  seeds/extraSeeds/
    data.py                      # All seed data (one place to add entries)
    run_all.py                   # Runs estructura → instructores → aprendices → actividades
    queries.py                   # SeedQueries enum with INSERT_* statements
```

### ENUM: estado_formacion_aprendiz
Values: `lectiva_en_curso` | `lectiva_concluida` | `productiva_en_curso` | `productiva_concluida` | `trasladado` | `suspendido`
- **Old boolean columns removed** in migration `20260407000001`. Do not use them.
- "In productive stage" = `estado IN ('productiva_en_curso', 'productiva_concluida')`

### Contrato de Aprendizaje
- `empresa_id` lives in `contrato_aprendizaje`, NOT in `ficha_aprendiz`
- `contrato_aprendizaje.estado` values: `'activo'` | `'terminado'` | `'cancelado'`
- CHECK constraint: `fecha_fin >= fecha_inicio` (validate server-side before inserting)

---

## Seed Data (extraSeeds)

### Credentials
All seed users share password: **Sena2024\***

### Instructors & Fichas
| Instructor | Email | Fichas |
|---|---|---|
| Juan Carlos Pérez | juan.perez@sena.edu.co | 2900001, 2900007, 2900008, 2900009 |
| María Fernanda López | maria.lopez@sena.edu.co | 2900002 |
| Carlos Alberto Rodríguez | carlos.rodriguez@sena.edu.co | 2900003 |
| Adriana Lucía Suárez | adriana.suarez@sena.edu.co | 2900004 |
| Ricardo Antonio Mendoza | ricardo.mendoza@sena.edu.co | 2900005 |
| Elena Patricia Beltrán | elena.beltran@sena.edu.co | 2900006 |

### Aprendices per Ficha
- **2900001**: ana.gomez (lectiva), luis.torres (productiva), mateo.julian (productiva)
- **2900002**: sofia.mendez (lectiva), andres.ruiz (productiva)
- **2900003**: camila.vargas (lectiva), miguel.castro (concluida)
- **2900004**: mario.duarte (lectiva), claudia.nieto (productiva)
- **2900005**: felipe.basto (lectiva), paola.ortiz (productiva)
- **2900006**: jorge.vivas (lectiva), diana.solano (concluida)
- **2900007**: valentina.rios, samuel.guerrero, isabella.mora, david.pineda, laura.espinosa (all productiva)
- **2900008**: nicolas.herrera, maria.gonzalez, sebastian.ramirez, juliana.cardenas, andres.mora (all productiva)
- **2900009**: camilo.suarez, paula.mendez, santiago.lopez, sara.rodriguez, juan.david (all productiva)

All aprendiz emails: `<name>@aprendiz.sena.edu.co`

---

## Migration History
| File | What it does |
|---|---|
| `20260323000001_initial_etapa_productiva.sql` | Creates `empresa`, `ficha_aprendiz`, `contrato_aprendizaje` |
| `20260323000002_remove_empresa_from_ficha_aprendiz.sql` | Removes empresa fields from ficha_aprendiz |
| `20260406000001_proceso_ep.sql` | Creates EP evaluation tables (ep_factor, proceso_ep, momentos 1/2/3) |
| `20260407000001_enum_estado_formacion.sql` | Replaces 4 booleans with `estado_formacion_aprendiz` ENUM |
| `20260408000001_add_unique_nombre_constraints.sql` | UNIQUE on `centro.nombre`, `coordinacion.nombre`, `area.nombre`, `programa_formacion.nombre` |
| `20260409000001_unique_actividades_seed.sql` | UNIQUE on `(nombre, fase_proyecto_id)`, `(nombre, actividad_proyecto_id)`, `(nombre, actividad_aprendizaje_id)` to prevent seed duplicates |
| `20260409000002_unique_fase_proyecto_seed.sql` | UNIQUE on `(nombre, proyecto_formativo_id)` in `fase_proyecto` to prevent seed duplicates |

---

## Known Issues Fixed
- **Seed duplicates**: `actividad_proyecto`, `actividad_aprendizaje`, `seccion_actividad` were being duplicated on every seed run because `ON CONFLICT DO NOTHING` without a column target never fires with new UUIDs. Fixed by adding UNIQUE constraints (migration `20260409000001`) and updating `queries.py` to use `ON CONFLICT (nombre, ...)`.
- **Missing UNIQUE constraints**: `ON CONFLICT (nombre)` in seeds for `centro`, `coordinacion`, `area`, `programa_formacion` failed until migration `20260408000001`.
- **`estado_formacion_aprendiz` ENUM**: Seeds must use string values like `'productiva_en_curso'`, not booleans.

---

## EP Instructor Flow
1. `/etapa-productiva/instructor/fichas` — list instructor's fichas
2. `/etapa-productiva/instructor/ficha/<id>` — ficha detail: aprendices tab + empresas tab
   - Aprendiz **without** contract → "Asignar contrato" button → `ep_contrato_crear`
   - Aprendiz **with** contract → "Gestionar proceso" button → `ep_gestionar_proceso`
3. `.../contrato/nuevo` — create contract (empresa dropdown = ficha's empresas, falls back to all)
4. `.../contrato/editar` — edit existing contract
5. `.../gestionar/iniciar` (POST) — starts EP process (requires active contract)
6. `.../proceso/<id>/momento-1/editar` — edit Momento 1 (Planning)
7. `.../proceso/<id>/momento-2/editar` — edit Momento 2 (Follow-up + evaluations)
8. `.../proceso/<id>/momento-3/editar` — edit Momento 3 (Final evaluation)
